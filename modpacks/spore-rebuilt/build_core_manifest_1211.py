"""Replace only verified core projects in the migration candidate."""
from pathlib import Path
import json

ROOT = Path(__file__).parent / "source_1211"
SRC = ROOT / "manifest-no-create.json"
DST = ROOT / "manifest-core-1211.json"

CORE = {
    678295: 7245666,
    1353462: 7539022,
    268560: 7904058,
    231951: 6733669,
    313970: 8993983,
    535291: 7204624,
    400514: 9067113,
}

def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    replaced = []
    present = set()
    for entry in data.get("files", []):
        project = entry.get("projectID")
        if project in CORE:
            entry["fileID"] = CORE[project]
            replaced.append(project)
            present.add(project)
    for project, file_id in CORE.items():
        if project not in present:
            data.setdefault("files", []).append({"projectID": project, "fileID": file_id, "required": True})
            replaced.append(project)
    data["name"] = "Parasite 1.21.1 NeoForge — core migration"
    data["files"] = [x for x in data.get("files", []) if x.get("projectID") != 328085]
    DST.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"replaced {len(replaced)} core entries: {sorted(set(replaced))}")
    print(f"left {len(data['files'])} entries for compatibility review")

if __name__ == "__main__":
    main()
