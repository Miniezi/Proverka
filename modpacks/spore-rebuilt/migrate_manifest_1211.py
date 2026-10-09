"""Create a safe intermediate manifest from the supplied CurseForge profile.

This intentionally does not invent file IDs. It removes Create and writes a
reviewable candidate; exact NeoForge 1.21.1 files are filled after validation.
"""
from pathlib import Path
import json

src = Path(__file__).parent / 'source_1211' / 'manifest.json'
dst = Path(__file__).parent / 'source_1211' / 'manifest-no-create.json'
d = json.loads(src.read_text())
d['name'] = 'Parasite 1.21.1 NeoForge — migration candidate'
d['minecraft']['version'] = '1.21.1'
d['minecraft']['modLoaders'] = [{'id': 'neoforge-21.1.x', 'primary': True}]
d['files'] = [f for f in d['files'] if f.get('projectID') != 328085]
dst.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print(f'wrote {dst} with {len(d["files"])} inherited entries')
