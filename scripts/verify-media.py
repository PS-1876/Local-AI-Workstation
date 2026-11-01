"""Read-only full SHA-256 verification of selected media catalog files."""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def verify(entry, root):
    root = root.resolve()
    relative = Path(entry["comfyui_model_subdir"]) / entry["filename"]
    path = (root / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(root):
        raise ValueError("Catalog entry escapes the selected model root")
    expected = entry["sha256"]
    if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("Catalog entry has an invalid SHA-256")
    if not path.is_file():
        return {"filename": entry["filename"], "status": "missing"}
    if path.stat().st_size != entry["bytes"]:
        return {"filename": entry["filename"], "status": "size_mismatch"}
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    actual = digest.hexdigest()
    return {"filename": entry["filename"], "status": "verified" if actual == expected else "sha256_mismatch", "sha256": actual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="ComfyUI model root, containing text_encoders, vae, etc.")
    parser.add_argument("--file", required=True, action="append", help="Exact catalog filename; repeat for additional files")
    parser.add_argument("--catalog", type=Path, default=Path(__file__).resolve().parents[1] / "models/media-sources.json")
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    names = set(args.file)
    entries = [entry for entry in catalog["files"] if entry["filename"] in names]
    if len(entries) != len(names) or {e["filename"] for e in entries} != names:
        parser.error("Every requested filename must have exactly one catalog entry")
    results = [verify(entry, args.root) for entry in entries]
    print(json.dumps({"checks": results, "scope": "artifact bytes only; no inference or workflow qualification"}, indent=2))
    return 0 if all(result["status"] == "verified" for result in results) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        sys.exit(2)
