"""Validate the generated 1.21.1 core manifest."""
from pathlib import Path
import json
import sys

MANIFEST = Path(__file__).parent / "source_1211" / "manifest-core-1211.json"
REQUIRED = {
    678295, 1353462, 268560, 231951, 313970,
    535291, 400514, 835091, 238222,
}

def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = data.get("files", [])
    projects = [x.get("projectID") for x in files]
    errors = []
    if data.get("minecraft", {}).get("version") != "1.21.1":
        errors.append("Minecraft version is not 1.21.1")
    if 328085 in projects:
        errors.append("Create is present")
    missing = sorted(REQUIRED - set(projects))
    if missing:
        errors.append(f"missing core project IDs: {missing}")
    duplicates = sorted({p for p in projects if projects.count(p) > 1})
    if duplicates:
        errors.append(f"duplicate project IDs: {duplicates}")
    if errors:
        print("FAIL")
        print("\n".join(f"- {x}" for x in errors))
        return 1
    print(f"PASS: {len(files)} entries, 9 core projects, no Create")
    return 0

if __name__ == "__main__":
    sys.exit(main())
