# MultiGPU reference patches

These two local compatibility patches derive from [pollockjj/ComfyUI-MultiGPU](https://github.com/pollockjj/ComfyUI-MultiGPU) commit `37a73feda5804045e4f39d8c640905d62a2169d1` (2.6.4). They are offered for opt-in qualification, not automatically applied. The upstream project was archived when reviewed on October 31, 2026. These are local modifications, not an upstream release or endorsement.

The derived patches retain upstream's [GNU GPL version 3 license](ComfyUI-MultiGPU.LICENSE). Preserve upstream copyright/attribution and license notices when distributing the patched source. This third-party scope is separate from the root project's original-material license decision. The license file is the exact pinned upstream text, SHA-256 `8b1ba204bb69a0ade2bfcf65ef294a920f6bb361b317dba43c7ef29d96332b9b`.

| Patch | Reason | Qualification limit |
| --- | --- | --- |
| [01 portable peer query](multigpu-01-portable-peer-query.patch) | Replaces the Linux-specific `libcudart.so` ctypes lookup with the documented `torch.cuda.can_device_access_peer` API | Does not enable peer access or prove a given GPU pair supports it; API errors still propagate |
| [02 preserve DLPack storage](multigpu-02-preserve-dlpack-storage.patch) | Guards the original tensor's device and preserves its storage instead of staging a replacement tensor | Real CUDA stream/kernel behavior and numerical/render output still need testing |

Both patches pass `git apply --check` against independently fetched pinned upstream files, and applied bytes match the reference modifications exactly. [Application evidence](patch-validation.json) records hashes. The [mock regression report](behavior-checks.json) has 10 passing patched checks and two expected upstream failures: loss of writes to original storage, and duplicate keyword argument failure. No real CUDA code or model generation ran in these tests. [PyTorch peer-query API](https://docs.pytorch.org/docs/stable/generated/torch.cuda.can_device_access_peer.html)

In a new isolated checkout at the exact commit, with a clean working tree, apply the patches in numbered order. Replace the absolute patch directory before running:

```powershell
$patchRoot = 'C:\path\to\Local-AI-Workstation\patches\comfyui-multigpu'
git apply --check (Join-Path $patchRoot 'multigpu-01-portable-peer-query.patch')
if ($LASTEXITCODE -ne 0) { throw 'Patch 01 does not apply' }
git apply (Join-Path $patchRoot 'multigpu-01-portable-peer-query.patch')
if ($LASTEXITCODE -ne 0) { throw 'Patch 01 failed' }
git apply --check (Join-Path $patchRoot 'multigpu-02-preserve-dlpack-storage.patch')
if ($LASTEXITCODE -ne 0) { throw 'Patch 02 does not apply' }
git apply (Join-Path $patchRoot 'multigpu-02-preserve-dlpack-storage.patch')
if ($LASTEXITCODE -ne 0) { throw 'Patch 02 failed' }
```

Do not run this against the already-patched reference installation or a different revision. Keep a separate unmodified source directory to run the CPU-only regression script:

```powershell
py -3.13 (Join-Path $patchRoot 'check_multigpu_patches.py') --upstream 'C:\AI-Test\MultiGPU-original' --patched 'C:\AI-Test\MultiGPU-patched' --output 'C:\AI-Test\patch-check.json'
```

Both directories must contain the corresponding `__init__.py` and `p2p_registry.py`. The script extracts selected definitions and supplies mock torch/kitchen objects. The JSON report is written only to the selected output path. A real image/video task and an observed device split remain required before these patches become a supported profile default.
