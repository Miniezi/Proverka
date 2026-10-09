from pathlib import Path
import json,zipfile,re
P=Path(__file__).resolve().parent;O=P/'overrides';D=O/'config/paxi/datapacks/quarantine_balance'
# Apotheosis requires min/max ranges to be exact multiples of their step.
for p in (D/'data/apotheosis/affixes').rglob('*.json'):
 d=json.loads(p.read_text())
 for v in d.get('values',{}).values():
  if isinstance(v,dict) and 'min' in v and 'max' in v:
   v['min']=round(v['min'],2);v['max']=round(v['max'],2);v['step']=.01 if v['max']>=v['min'] else -.01
 p.write_text(json.dumps(d,indent=2)+'\n')
# Source gunpack contains an obsolete pre-1.1 format: exclude it.
for base in [O/'tacz',P/'server/tacz']:(base/'Nitrogen_Gunpack_0925.zip').unlink(missing_ok=True)
# Remove only broken indexes and unsupported vehicle workbench data from personal copies.
removed={};modified={}
for f in (O/'tacz').glob('*.zip'):
 with zipfile.ZipFile(f) as z:
  contents={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
 bad=['data/mw19/index/guns/jak12.json','data/qkl/index/attachments/mu73_bayonet.json']
 bad += [n for n in contents if n.startswith('data/bf1/index/blocks/') or n=='data/bf1/data/blocks/telegraph.json' or n.startswith('data/bf1/recipes/block/')]
 removed[f.name]=[n for n in bad if n in contents]
 for n in bad:contents.pop(n,None)
 for n,b in list(contents.items()):
  if n.endswith('.json') and n.startswith('data/mw19/index/guns/') and b'mw19:default_gun_logic' in b:
   contents[n]=b.replace(b'mw19:default_gun_logic',b'tacz:default_gun_logic');modified.setdefault(f.name,[]).append(n)
 tmp=f.with_suffix('.tmp')
 with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in contents.items():z.writestr(n,b)
 with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
 tmp.replace(f)
# Spore optional cross-mod recipes lack load conditions in the upstream release.
for jar in (P/'mods').glob('*.jar'):
 with zipfile.ZipFile(jar) as z:
  for n in z.namelist():
   if n.startswith(('data/create/recipe/','data/farmersdelight/recipe/')) and n.endswith('.json'):
    d=json.loads(z.read(n));d['neoforge:conditions']=[{'type':'neoforge:mod_loaded','modid':n.split('/')[1]}]
    dst=D/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(d,indent=2)+'\n')
(P/'resource-fixes.json').write_text(json.dumps({'removed_broken_indexes':removed,'script_namespace_fixes':modified,'excluded_pack':'Nitrogen_Gunpack_0925.zip'},indent=2))
print('Fixed affix steps; gunpack index and optional recipe corrections written')
