"""Reproducible MIT data port of Minigato668's MINI additions 1.4.0."""
import json,re,zipfile,hashlib,urllib.request,shutil,sys,io,gzip,uuid
from pathlib import Path
import nbtlib as n
P=Path(__file__).resolve().parent
PIN=json.loads((P/'upstream.json').read_text())
archive=P/'upstream.jar'
if not archive.exists():urllib.request.urlretrieve(PIN['url'],archive)
assert hashlib.sha512(archive.read_bytes()).hexdigest()==PIN['hashes']['sha512']
alternative_tags={}
OUT=P/'generated';shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir()
renames={'advancements':'advancement','recipes':'recipe','loot_tables':'loot_table','functions':'function','structures':'structure','items':'item','blocks':'block','entity_types':'entity_type','fluids':'fluid','game_events':'game_event'}
def attr(s):
 s=str(s)
 return {'forge:step_height_addition':'minecraft:generic.step_height','forge:swim_speed':'neoforge:swim_speed','forge:entity_gravity':'minecraft:generic.gravity'}.get(s,s if ':' in s else 'minecraft:'+s)
def components(t,item='minecraft:item_frame'):
 t=n.Compound(t);c=n.Compound()
 d=t.pop('display',{})
 if 'Name' in d:c['minecraft:custom_name']=d['Name']
 if 'Lore' in d:c['minecraft:lore']=d['Lore']
 if 'color' in d:c['minecraft:dyed_color']=n.Compound({'rgb':n.Int(d['color'])})
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
 if isinstance(d,str):
  return d.replace('forge:tools/knives','c:tools/knife').replace('forge:shears','c:tools/shear').replace('forge:dough','c:doughs').replace('farmersdelight:tool_action','farmersdelight:item_ability')
 if not isinstance(d,dict):return d
 d={k:jsonfix(v) for k,v in d.items()}
 if str(d.get('type','')).startswith(('minecraft:crafting_', 'minecraft:smelting', 'minecraft:blasting', 'minecraft:campfire_cooking', 'minecraft:smoking', 'create:', 'farmersdelight:')):
  for key in ['processingTime','heatRequirement','transitionalItem']:
   if key in d:d[{'processingTime':'processing_time','heatRequirement':'heat_requirement','transitionalItem':'transitional_item'}[key]]=d.pop(key)
  for key in ['result','results','transitional_item','container']:
   if key not in d:continue
   if isinstance(d[key],str):d[key]={'id':d[key]}
   for v in d[key] if isinstance(d[key],list) else [d[key]]:
    if isinstance(v,dict):
     if 'item' in v and isinstance(v['item'],str):v['id']=v.pop('item')
     if 'fluid' in v:v['id']=v.pop('fluid')
  if 'ingredients' in d:
   for i,ingredient in enumerate(d['ingredients']):
    if isinstance(ingredient,list):
     ident='alternatives/'+hashlib.sha256(json.dumps(ingredient,sort_keys=True).encode()).hexdigest()[:16]
     alternative_tags[ident]=[v['item'] if 'item' in v else '#'+v['tag'] for v in ingredient]
     d['ingredients'][i]={'tag':'sporeminiadditions:'+ident}
  if str(d.get('type','')).startswith('create:'):
   for v in d.get('ingredients',[]):
    if isinstance(v,dict) and 'fluid' in v:v['type']='neoforge:single';v.pop('nbt',None)
  if d.get('type')=='farmersdelight:cutting':
   d['result']=[{'item':{k:v for k,v in item.items() if k!='chance'},**({'chance':item['chance']} if 'chance' in item else {})} for item in d['result']]
   if isinstance(d.get('sound'),str):d['sound']={'sound_id':d['sound']}
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
  parts=[part.lower() for part in parts]
  path=OUT.joinpath(*parts);path.parent.mkdir(parents=True,exist_ok=True);raw=z.read(name)
  if name.endswith('.mcfunction'):
   raw=('\n'.join(command(l) for l in raw.decode().splitlines())+'\n').encode()
   if parts[-1]=='wsp.mcfunction':raw=('$witherstormmod ultimateTarget set $(storm) @e[type=spore:proto,limit=1,sort=nearest]\nexecute as @e[type=#sporeminiadditions:wither_storm] at @s run effect give @e[distance=..10] minecraft:wither 30 4 true\n$execute as @e[type=#sporeminiadditions:wither_storm] at @s run effect give @e[distance=..50] $(effect) infinite 0 true\n').encode()
   if parts[-1]=='proto_count3.mcfunction':raw=raw.replace(b'execute as @e[type=spore:proto] run function inqui:wsp',b'execute if entity @e[type=#sporeminiadditions:wither_storm] as @e[type=spore:proto] run function inqui:wsp {storm:"@w",effect:"witherstormmod:wither_sickness"}')
   raw=raw.replace(b'type=touhou_little_maid:maid',b'type=#sporeminiadditions:maid')
  elif name.endswith('.json'):
   d=jsonfix(json.loads(raw))
   if parts[2]=='advancement' and 'display' in d:
    ic=d['display']['icon']
    if 'item' in ic:ic['id']=ic.pop('item')
   if parts[2]=='tags':
    d['values']=[{'id':v,'required':False} if isinstance(v,str) and v.lstrip('#').split(':')[0] not in ['minecraft','spore','inqui','sporeminiadditions'] else v for v in d.get('values',[])]
   # Missing optional mods must not invalidate base recipes/loot tables.
   if parts[1] in ['create','farmersdelight','incendium','witherstormmod'] and parts[2] in ['recipe','loot_table','loot_modifiers']:
    d['neoforge:conditions']=[{'type':'neoforge:mod_loaded','modid':parts[1]}]
   raw=(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
  if name.endswith('.nbt') and '/inqui/' in name:
   structure=n.File.parse(io.BytesIO(gzip.decompress(raw)))
   changed=False
   for entry in structure.get('entities',[]):
    e=entry['nbt']
    # Vanilla DFU has no schema for modded entity IDs. Migrate these explicitly.
    if not str(e.get('id','')).startswith('spore:'):continue
    changed=True;entity(e)
    if 'ActiveEffects' in e:
     effects=[]
     for old in e.pop('ActiveEffects'):
      assert 'forge:id' in old, 'Unresolved numeric effect ID'
      new=n.Compound({'id':old['forge:id']})
      for before,after in [('Amplifier','amplifier'),('Duration','duration'),('Ambient','ambient'),('ShowParticles','show_particles'),('ShowIcon','show_icon')]:
       if before in old:new[after]=old[before]
      effects.append(new)
     e['active_effects']=n.List[n.Compound](effects)
    if 'Attributes' in e:e['Attributes']=n.List[n.Compound]([a for a in e['Attributes'] if not (str(a.get('Name'))=='forge:step_height_addition' and float(a.get('Base',0))==0 and not a.get('Modifiers'))])
    for attribute in e.get('Attributes',[]):
     attribute['Name']=n.String(attr(attribute['Name']))
     for modifier in attribute.get('Modifiers',[]):
      old=n.Compound(modifier);modifier.clear()
      modifier['id']=n.String('sporeminiadditions:legacy_'+uuid.UUID(bytes=b''.join((int(v)&0xffffffff).to_bytes(4,'big') for v in old['UUID'])).hex)
      modifier['amount']=old['Amount'];modifier['operation']=n.String(['add_value','add_multiplied_base','add_multiplied_total'][int(old['Operation'])])
   if changed:
    stream=io.BytesIO();structure.write(stream);raw=gzip.compress(stream.getvalue(),mtime=0)
  path.write_bytes(raw)
for tag,value in [('maid','touhou_little_maid:maid'),('wither_storm','witherstormmod:wither_storm')]:
 path=OUT/'data/sporeminiadditions/tags/entity_type'/f'{tag}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({'values':[{'id':value,'required':False}]}))
for ident,values in alternative_tags.items():
 path=OUT/'data/sporeminiadditions/tags/item'/f'{ident}.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps({'values':[{'id':v,'required':False} for v in values]}))
expected=[]
for path in OUT.glob('data/*/recipe/**/*.json'):
 namespace=path.relative_to(OUT).parts[1];name=path.relative_to(OUT/'data'/namespace/'recipe').with_suffix('').as_posix()
 expected.append((namespace if namespace in ['create','farmersdelight'] else 'spore')+'|'+namespace+':'+name)
check=P/'harness/src/main/resources/expected-recipes.txt';check.parent.mkdir(parents=True,exist_ok=True);check.write_text('\n'.join(sorted(expected)))
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
