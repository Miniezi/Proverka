from pathlib import Path
import json,zipfile,hashlib,tomllib
R=Path(__file__).resolve().parent
index=json.loads((R/'index.json').read_text());resolved=json.loads((R/'resolved.json').read_text())
mods=['# Моды Spore Rebuilt 1.1.0','', '| Мод | Версия | Дата файла |','|---|---|---|']
for x in sorted(resolved.values(),key=lambda x:x['project']['title'].casefold()):
 p,v=x['project'],x['version'];mods.append(f"| [{p['title']}](https://modrinth.com/mod/{p['slug']}) | {v['version_number']} | {v['date_published'][:10]} |")
mods.append('| Spore Rebuilt Fixes (встроен) | 1.0.0 | 2026-10-09 |')
mods.append('| Spore Apotheosis Balance (встроен) | 1.0.0 | 2026-10-09 |')
(R/'MODS.md').write_text('\n'.join(mods)+'\n')
paths=set()
for f in index['files']:
 assert f['path'] not in paths;paths.add(f['path'])
 assert '..' not in Path(f['path']).parts and not f['path'].startswith('/')
 p=R/'downloads'/f['path'];assert p.exists(),p
 b=p.read_bytes()
 if f.get('env',{}).get('server')!='unsupported': assert len(b)==f['fileSize']
 if f.get('env',{}).get('server')!='unsupported':
  for a,h in f['hashes'].items():assert hashlib.new(a,b).hexdigest()==h,f['path']
for p in (R/'overrides').rglob('*'):
 if p.suffix=='.json':json.loads(p.read_text())
 if p.suffix=='.toml':tomllib.loads(p.read_text())
out=R/'output/Spore-Rebuilt-1.1.0.mrpack';out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
 z.writestr('modrinth.index.json',json.dumps(index,ensure_ascii=False,indent=2))
 for p in sorted((R/'overrides').rglob('*')):
  if p.is_file():z.write(p,p.relative_to(R))
 for name in ['README_RU.md','MODS.md','VALIDATION.md']:
  z.write(R/name,'overrides/Spore-Rebuilt/'+name)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert 'modrinth.index.json' in z.namelist()
print(json.dumps({'file':str(out),'bytes':out.stat().st_size,'mods':len(resolved)+2,'download_entries':len(index['files']),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
