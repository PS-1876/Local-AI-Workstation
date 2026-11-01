"""CPU-only checks for two reference patches; no ComfyUI or torch imports.

Only selected definitions are compiled from the inspected source files.
Mock objects check peer-query routing/cache behavior and DLPack storage identity.
These checks do not establish CUDA kernel, stream, numerical, or video correctness.
"""

import argparse
import ast
import contextlib
import json
import logging
from pathlib import Path
import sys
import types


def definition(path, name, namespace):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    matches = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name]
    if len(matches) != 1:
        raise AssertionError(f"Expected exactly one {name} definition")
    module = ast.fix_missing_locations(ast.Module(body=matches, type_ignores=[]))
    exec(compile(module, str(path), "exec"), namespace)
    return namespace[name]


def peer_checks(stage):
    calls = []
    available = [True]

    def query(src, dst):
        calls.append((src, dst))
        return src == 0 and dst == 1

    fake_torch = types.SimpleNamespace(cuda=types.SimpleNamespace(
        is_available=lambda: available[0], can_device_access_peer=query
    ))
    cls = definition(stage / "p2p_registry.py", "MultiGPUP2PRegistry", {
        "torch": fake_torch, "logger": logging.getLogger("mock-peer")
    })
    registry = cls()
    checks = []

    def record(name, condition):
        checks.append({"name": name, "passed": bool(condition)})

    record("same device returns true without native query", registry.can_access_peer(0, 0) is True and not calls)
    record("cross-device result comes from documented torch API", registry.can_access_peer(0, 1) is True and calls == [(0, 1)])
    record("repeated pair uses cache", registry.can_access_peer(0, 1) is True and calls == [(0, 1)])
    record("reverse pair is independently queried", registry.can_access_peer(1, 0) is False and calls == [(0, 1), (1, 0)])
    registry.clear_cache()
    registry.can_access_peer(0, 1)
    record("clear_cache permits a new query", calls == [(0, 1), (1, 0), (0, 1)])
    available[0] = False
    before = len(calls)
    record("unavailable CUDA returns false without peer query", registry.can_access_peer(2, 3) is False and len(calls) == before)
    return checks


class FakeDevice:
    def __init__(self, kind, index=None):
        self.type = kind
        self.index = index


class FakeTensor:
    def __init__(self, device, transfers):
        self.device = device
        self.storage = {"value": 0}
        self.transfers = transfers

    def to(self, device):
        self.transfers.append(device)
        if isinstance(device, str):
            device = FakeDevice(device)
        other = FakeTensor(device, self.transfers)
        other.storage["value"] = self.storage["value"]
        return other


def dlpack_case(root, keyword, tensor_index, expect_peer_access=False):
    transfers, guards, wraps = [], [], []
    tensor = FakeTensor(FakeDevice("cuda", tensor_index), transfers)

    def wrap_for_dlpack(tensor):
        wraps.append(tensor)
        tensor.storage["value"] = 73
        return {"storage_owner": tensor}

    kitchen = types.SimpleNamespace(_wrap_for_dlpack=wrap_for_dlpack)

    @contextlib.contextmanager
    def guard(device, reason=None):
        guards.append((device.type, device.index))
        yield

    package_name = "isolated_patch_test"
    package = types.ModuleType(package_name)
    package.__path__ = []
    peer_module = types.ModuleType(package_name + ".p2p_registry")
    peer_module.p2p_registry = types.SimpleNamespace(can_access_peer=lambda a, b: expect_peer_access)
    old_package = sys.modules.get(package_name)
    old_peer = sys.modules.get(package_name + ".p2p_registry")
    sys.modules[package_name] = package
    sys.modules[package_name + ".p2p_registry"] = peer_module
    namespace = {
        "__package__": package_name,
        "importlib": types.SimpleNamespace(import_module=lambda name: kitchen),
        "logger": logging.getLogger("mock-dlpack"),
        "cuda_device_guard": guard,
        "get_current_device": lambda: FakeDevice("cuda", 0),
        "_coerce_torch_device": lambda value: value,
    }
    error = None
    result = None
    idempotent = False
    try:
        patch = definition(root / "__init__.py", "_patch_comfy_kitchen_dlpack_device_guard", namespace)
        assert patch() is True
        wrapper = kitchen._wrap_for_dlpack
        assert patch() is True
        idempotent = kitchen._wrap_for_dlpack is wrapper
        result = wrapper(tensor=tensor) if keyword else wrapper(tensor)
    except Exception as exc:
        error = type(exc).__name__
    finally:
        for name, previous in [(package_name, old_package), (package_name + ".p2p_registry", old_peer)]:
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous
    return {
        "keyword_tensor": keyword,
        "tensor_device": tensor_index,
        "mock_execution_device": 0,
        "mock_peer_access": expect_peer_access,
        "passed": error is None and result["storage_owner"] is tensor and wraps == [tensor]
            and tensor.storage["value"] == 73 and not transfers
            and guards == [("cuda", tensor_index)] and idempotent,
        "exception_type": error,
        "transfer_count": len(transfers),
        "original_storage_value": tensor.storage["value"],
        "guard_devices": guards,
        "patch_idempotent": idempotent,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--patched", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    peer = peer_checks(args.patched)
    patched = [dlpack_case(args.patched, keyword, device) for keyword, device in [(False, 1), (True, 1), (False, 0), (True, 0)]]
    upstream = [dlpack_case(args.upstream, keyword, 1) for keyword in [False, True]]
    report = {
        "scope": "CPU-only mock regression checks; no torch import, CUDA calls, ComfyUI import, service changes, or model jobs.",
        "patched_peer_checks": peer,
        "patched_dlpack_cases": patched,
        "upstream_negative_controls": upstream,
        "patched_pass_count": sum(x["passed"] for x in peer + patched),
        "patched_check_count": len(peer + patched),
        "negative_control_regressions_detected": all(not x["passed"] for x in upstream),
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all(x["passed"] for x in peer + patched) or not report["negative_control_regressions_detected"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
