"""Reproducible MIT data port of Minigato668's MINI additions 1.4.0."""
import json,re,zipfile,hashlib,urllib.request,shutil,sys
from pathlib import Path
import nbtlib as n
P=Path(__file__).resolve().parent
PIN=json.loads((P/'upstream.json').read_text())
archive=P/'upstream.jar'
if not archive.exists():urllib.request.urlretrieve(PIN['url'],archive)
assert hashlib.sha512(archive.read_bytes()).hexdigest()==PIN['hashes']['sha512']
OUT=P/'generated';shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir()
renames={'advancements':'advancement','recipes':'recipe','loot_tables':'loot_table','functions':'function','structures':'structure','items':'item','blocks':'block','entity_types':'entity_type','fluids':'fluid','game_events':'game_event'}
def attr(s):
 s=str(s)
 return {'forge:step_height_addition':'minecraft:generic.step_height','forge:swim_speed':'neoforge:swim_speed'}.get(s,s if ':' in s else 'minecraft:'+s)
def components(t,item='minecraft:item_frame'):
 t=n.Compound(t);c=n.Compound()
 d=t.pop('display',{})
 if 'Name' in d:c['minecraft:custom_name']=d['Name']
 if 'Lore' in d:c['minecraft:lore']=d['Lore']
 for old,new in [('Enchantments','enchantments'),('StoredEnchantments','stored_enchantments')]:
  if old in t:c['minecraft:'+new]=n.Compound({'levels':n.Compound({str(e['id']):n.Int(e['lvl']) for e in t.pop(old)})})
 if 'AttributeModifiers' in t:
  mods=[]
  for i,m in enumerate(t.pop('AttributeModifiers')):
   mods.append(n.Compound({'type':n.String(attr(m['AttributeName'])),'id':n.String('sporeminiadditions:'+str(m.get('Slot','any'))+'_'+str(i)),'amount':n.Double(m['Amount']),'operation':n.String(['add_value','add_multiplied_base','add_multiplied_total'][int(m['Operation'])]),'slot':m.get('Slot',n.String('any'))}))
  c['minecraft:attribute_modifiers']=n.Compound({'modifiers':n.List[n.Compound](mods)})
 if 'SkullOwner' in t:
  sk=t.pop('SkullOwner');pr=n.Compound()
  if 'Id' in sk:pr['id']=sk['Id']
  if 'Name' in sk:pr['name']=sk['Name']
  pr['properties']=n.List[n.Compound]([n.Compound({'name':n.String(name),'value':v['Value']}) for name,values in sk.get('Properties',{}).items() for v in values])
  c['minecraft:profile']=pr
 if 'EntityTag' in t:
  e=t.pop('EntityTag');e.setdefault('id',n.String(item));c['minecraft:entity_data']=e
 for old,new in [('Damage','damage'),('CustomModelData','custom_model_data'),('RepairCost','repair_cost')]:
  if old in t:c['minecraft:'+new]=n.Int(t.pop(old))
 if 'Unbreakable' in t:
  if t.pop('Unbreakable'):c['minecraft:unbreakable']=n.Compound()
 if t:c['minecraft:custom_data']=t
 return c

def entity(v):
 if isinstance(v,n.Compound):
  for k in list(v):v[k]=entity(v[k])
  if 'tag' in v and ('id' in v or set(v)=={'tag'}):v['components']=components(v.pop('tag'),str(v.get('id','minecraft:item_frame')))
  if 'id' in v and 'Count' in v:v['count']=n.Int(v.pop('Count'))
 elif isinstance(v,n.List):
  for i in range(len(v)):v[i]=entity(v[i])
 return v

def balanced(s,start):
 depth=0;quote=None;escaped=False
 for i in range(start,len(s)):
  ch=s[i]
  if quote:
   if escaped:escaped=False
   elif ch=='\\':escaped=True
   elif ch==quote:quote=None
  elif ch in "\"'":quote=ch
  elif ch=='{':depth+=1
  elif ch=='}':
   depth-=1
   if depth==0:return i+1
 raise ValueError(s)

def command(line):
 if line.lstrip().startswith('#'):return line
 # Item arguments in give/item replace; selectors are converted separately.
 pattern=r'((?:give\s+\S+\s+|with\s+)([a-z0-9_.-]+:[a-z0-9_./-]+))\{'
 m=re.search(pattern,line)
 if m:
  a=m.end()-1;b=balanced(line,a);c=components(n.parse_nbt(line[a:b]),m[2]);line=line[:a]+'['+','.join(k+'='+v.snbt() for k,v in c.items())+']'+line[b:]
 pos=0
 while True:
  m=re.search(r'nbt=!?\{',line[pos:])
  if not m:break
  a=pos+m.end()-1;b=balanced(line,a);t=entity(n.parse_nbt(line[a:b]));new=t.snbt();line=line[:a]+new+line[b:];pos=a+len(new)
 # Summoned entities use new item stack encoding.
 m=re.search(r'\bsummon\s+\S+\s+\S+\s+\S+\s+\S+\s+(\{)',line)
 if m:
  a=m.start(1);b=balanced(line,a);line=line[:a]+entity(n.parse_nbt(line[a:b])).snbt()+line[b:]
 return line

def jsonfix(d):
 if isinstance(d,list):return [jsonfix(x) for x in d]
 if not isinstance(d,dict):return d
 d={k:jsonfix(v) for k,v in d.items()}
 if d.get('function')=='minecraft:set_nbt':
  c=components(n.parse_nbt(d.pop('tag')));d['function']='minecraft:set_components';d['components']=json.loads(json.dumps(c.unpack(),default=int))
 if d.get('condition')=='minecraft:entity_properties':
  if d.get('entity')=='killer':d['entity']='attacker'
  for item in d.get('predicate',{}).get('equipment',{}).values():
   if 'tag' in item:item['items']='#'+item.pop('tag')
 return d

with zipfile.ZipFile(archive) as z:
 for name in z.namelist():
  if name.endswith('/') or not name.startswith(('data/','background.png')):continue
  parts=name.split('/')
  if name.startswith('data/'):
   if len(parts)>2:parts[2]=renames.get(parts[2],parts[2])
   if len(parts)>3 and parts[2]=='tags':parts[3]=renames.get(parts[3],parts[3])
  path=OUT.joinpath(*parts);path.parent.mkdir(parents=True,exist_ok=True);raw=z.read(name)
  if name.endswith('.mcfunction'):
   raw=('\n'.join(command(l) for l in raw.decode().splitlines())+'\n').encode()
   if parts[-1]=='wsp.mcfunction':raw=b'# Wither Storm integration requires its 1.21.1 port; core does not depend on it.\n'
  elif name.endswith('.json'):
   d=jsonfix(json.loads(raw))
   if parts[2]=='advancement' and 'display' in d:
    ic=d['display']['icon']
    if 'item' in ic:ic['id']=ic.pop('item')
   if parts[2]=='recipe':
    for key in ['result','results']:
     if key not in d:continue
     if isinstance(d[key],str):d[key]={'id':d[key]}
     for v in d[key] if isinstance(d[key],list) else [d[key]]:
      if isinstance(v,dict) and 'item' in v:v['id']=v.pop('item')
   # Missing optional mods must not invalidate base recipes/loot tables.
   if parts[1] in ['create','farmersdelight','incendium','witherstormmod'] and parts[2] in ['recipe','loot_table','loot_modifiers']:
    d['neoforge:conditions']=[{'type':'neoforge:mod_loaded','modid':parts[1]}]
   raw=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
  path.write_bytes(raw)
# Preserve structure DataVersion=3465: Minecraft's official data fixer migrates embedded entities and inventory.
(OUT/'pack.mcmeta').write_text(json.dumps({'pack':{'pack_format':48,'description':'MINI additions 1.4.0 — unofficial NeoForge 1.21.1 port; original by Minigato668'}}))
(OUT/'META-INF').mkdir()
(OUT/'META-INF/neoforge.mods.toml').write_text('''modLoader="lowcodefml"
loaderVersion="[1,)"
license="MIT"
[[mods]]
modId="sporeminiadditions"
version="1.4.0-port.1"
displayName="Spore MINI additions (Unofficial 1.21.1 Port)"
authors="Minigato668 (original); unofficial compatibility port"
logoFile="background.png"
description="Unofficial port of MINI additions 1.4.0 for NeoForge 1.21.1."
[[dependencies.sporeminiadditions]]
modId="minecraft"
type="required"
versionRange="[1.21.1,1.21.2)"
ordering="NONE"
side="BOTH"
[[dependencies.sporeminiadditions]]
modId="neoforge"
type="required"
versionRange="[21.1,)"
ordering="NONE"
side="BOTH"
[[dependencies.sporeminiadditions]]
modId="spore"
type="required"
versionRange="[2.2.0,)"
ordering="AFTER"
side="BOTH"
''')
for file in ['LICENSE','README_RU.md']:
 if (P/file).exists():shutil.copyfile(P/file,OUT/file)
(P/'dist').mkdir(exist_ok=True)
with zipfile.ZipFile(P/'dist/spore_mini_additions-1.4.0-port.1-neoforge-1.21.1.jar','w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(OUT.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(OUT))
print('PORT_BUILT',len(list(OUT.rglob('*.mcfunction'))),'functions')
