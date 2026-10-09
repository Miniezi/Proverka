from pathlib import Path
import zipfile,json
R=Path(__file__).resolve().parent
out=R/'overrides/mods/spore_rebuilt_fixes-1.0.0.jar';out.parent.mkdir(parents=True,exist_ok=True)
files={}
files['META-INF/mods.toml']='''modLoader="lowcodefml"
loaderVersion="[47,)"
license="MIT"
[[mods]]
modId="spore_rebuilt_fixes"
version="1.0.0"
displayName="Spore Rebuilt Fixes"
description="Recipe compatibility fixes for the Spore Rebuilt modpack."
[[dependencies.spore_rebuilt_fixes]]
modId="spore"
mandatory=true
versionRange="[2.2.0j]"
ordering="AFTER"
side="BOTH"
[[dependencies.spore_rebuilt_fixes]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1]"
ordering="NONE"
side="BOTH"
'''
files['pack.mcmeta']=json.dumps({'pack':{'pack_format':15,'description':'Spore Rebuilt recipe compatibility'}})
# Correct 1.21 result syntax inadvertently used in these 1.20.1 Spore recipes.
source=R/'downloads/mods/spore_1.20.1_2.2.0j.jar'
if not source.exists():source=R/'server/mods/spore_1.20.1_2.2.0j.jar'
with zipfile.ZipFile(source) as z:
 for name in ['halogen_light','broken_halogen_light']:
  path=f'data/spore/recipes/{name}.json';d=json.loads(z.read(path));d['result']['item']=d['result'].pop('id');files[path]=json.dumps(d,indent=2)
 # Optional integration recipes should only load when their target mod exists.
 for path in z.namelist():
  if '/recipes/' not in path or not path.endswith('.json'):continue
  d=json.loads(z.read(path))
  dep='create' if d.get('type','').startswith('create:') else ('farmersdelight' if path.startswith('data/farmersdelight/') else None)
  if dep:
   d.setdefault('conditions',[]).append({'type':'forge:mod_loaded','modid':dep});files[path]=json.dumps(d,indent=2)
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,s in sorted(files.items()):
  i=zipfile.ZipInfo(name,(2026,10,9,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,s)
print('Fix mod:',len(files),'files',out.stat().st_size,'bytes')
