"""Validate the intermediate CurseForge manifest before a real 1.21.1 build."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).parent / "source_1211"
MANIFEST = ROOT / "manifest-no-create.json"
CREATE_PROJECT = 328085

def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = []
    mc = data.get("minecraft", {})
    if mc.get("version") != "1.21.1":
        errors.append(f"minecraft.version={mc.get('version')!r}, expected '1.21.1'")
    loaders = [x.get("id", "") for x in mc.get("modLoaders", [])]
    if not any(x.startswith("neoforge-") for x in loaders):
        errors.append("no NeoForge loader declared")
    files = data.get("files", [])
    if any(x.get("projectID") == CREATE_PROJECT for x in files):
        errors.append("Create project is still present")
    missing = [i for i, x in enumerate(files) if not x.get("projectID") or not x.get("fileID")]
    if missing:
        errors.append(f"entries without projectID/fileID: {missing[:8]}")
    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        return 1
    print(f"PASS: {len(files)} inherited entries; NeoForge 1.21.1 declared; Create absent")
    print("NOTE: file IDs still require per-mod 1.21.1 compatibility verification.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
