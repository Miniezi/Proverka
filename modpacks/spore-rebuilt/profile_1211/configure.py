from pathlib import Path
import json,zipfile,copy,shutil,hashlib
P=Path(__file__).resolve().parent;O=P/'overrides';O.mkdir(exist_ok=True)
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
S=O/'config/puffish_skills'
write(S/'config.json',{'version':3,'show_warnings':True,'categories':['survival']})
C=S/'categories/survival'
write(C/'category.json',{'title':'Карантин: выживание','description':'Опыт за бои. 60 навыков; выбирай защиту, мобильность или ближний бой.','icon':{'type':'item','data':{'item':'minecraft:iron_sword'}},'background':'minecraft:textures/gui/advancements/backgrounds/stone.png','unlocked_by_default':True,'exclusive_root':False,'starting_points':1,'spent_points_limit':60})
defs={};skills={};links=[]
branches=[('vitality','Живучесть','golden_apple','generic.max_health',.5,'addition'),('armor','Защита','iron_chestplate','generic.armor',.25,'addition'),('speed','Подвижность','leather_boots','generic.movement_speed',.01,'multiply_base'),('damage','Ближний бой','iron_sword','generic.attack_damage',.02,'multiply_base'),('haste','Темп атаки','iron_axe','generic.attack_speed',.01,'multiply_base'),('resistance','Устойчивость','shield','generic.knockback_resistance',.015,'addition')]
for bi,(key,title,item,attr,value,op) in enumerate(branches):
 for i in range(1,11):
  sid=f'{key}_{i}'
  defs[sid]={'title':f'{title} {i}/10','description':f'Каждый ранг: +{value:g} ({op}).','icon':{'type':'item','data':{'item':'minecraft:'+item}},'frame':{'type':'advancement','data':{'frame':'challenge' if i==10 else 'task'}},'cost':1,'rewards':[{'type':'puffish_skills:attribute','data':{'attribute':'minecraft:'+attr,'value':value,'operation':op}}]}
  skills[sid]={'x':bi*68-170,'y':(i-1)*40,'definition':sid,'root':i==1}
  if i>1:links.append([f'{key}_{i-1}',sid])
write(C/'definitions.json',defs);write(C/'skills.json',skills);write(C/'connections.json',links)
write(C/'experience.json',{'level_limit':59,'experience_per_level':{'type':'expression','data':{'expression':'100 + level * 30'}},'sources':[{'type':'puffish_skills:kill_entity','data':{'variables':{'dropped_xp':{'operations':[{'type':'get_dropped_experience'}]}},'experience':'min(dropped_xp, 30)','anti_farming':{'limit_per_chunk':12,'reset_after_seconds':300}}}]})
# Apotheosis 8.x: preserve its built-in world-tier gates and scale attribute rewards.
D=O/'config/paxi/datapacks/quarantine_balance'
write(D/'pack.mcmeta',{'pack':{'pack_format':48,'description':'Quarantine: Apotheosis 8.9 balance and Spore invaders'}})
z=zipfile.ZipFile(next((P/'mods').glob('Apotheosis*')));changes=[]
def scale(v,f):
 if isinstance(v,bool):return v
 if isinstance(v,(int,float)):return round(v*f,5)
 if isinstance(v,dict):return {k:scale(x,f) for k,x in v.items()}
 if isinstance(v,list):return [scale(x,f) for x in v]
 return v
for n in z.namelist():
 if n.startswith('data/apotheosis/affixes/') and n.endswith('.json'):
  d=json.loads(z.read(n))
  if d.get('type')=='apotheosis:attribute' and 'values' in d:
   d['values']=scale(d['values'],.65);write(D/n,d);changes.append(n)
 if n.startswith('data/apotheosis/gems/') and n.endswith('.json'):
  d=json.loads(z.read(n));changed=False
  for bonus in d.get('bonuses',[]):
   if bonus.get('type') in ['apotheosis:attribute','apotheosis:durability'] and 'values' in bonus:
    bonus['values']=scale(bonus['values'],.65);changed=True
  if changed:write(D/n,d);changes.append(n)
base=json.loads(z.read('data/apotheosis/apothic_invaders/overworld/zombie.json'))
for entity in ['inf_human','inf_husk','inf_villager','inf_pillager']:
 d=copy.deepcopy(base);d['entity']='spore:'+entity;d['basic_data']['weights']['weight']=20
 for rarity,stats in d['stats'].items():
  for m in stats.get('attribute_modifiers',[]):
   if m['attribute']=='minecraft:generic.max_health':m['value']=scale(m['value'],.75)
   if m['attribute']=='minecraft:generic.attack_damage':m['value']=scale(m['value'],.6)
 write(D/f'data/apotheosis/apothic_invaders/overworld/spore_{entity}.json',d)
write(P/'balance-report.json',{'attribute_affix_and_gem_factor':.65,'changed_resources':changes,'spore_invaders':['spore:'+x for x in ['inf_human','inf_husk','inf_villager','inf_pillager']],'skills':60,'world_tier_gates':'original Apotheosis 8.9','runtime_validated':False})
(O/'options.txt').write_text('lang:ru_ru\nrenderDistance:10\nsimulationDistance:6\nentityDistanceScaling:0.75\n')
# Preserve uploaded gun archives verbatim; reject duplicate gameplay definitions.
source=P.parent/'source_1211/overrides/tacz';target=O/'tacz';target.mkdir(exist_ok=True)
selected=['Apocalypse_v1.1.7_G.zip','ARIPS_ver.1.3.0.zip','ChocolateMan V1.2.6a1-Public Edition.zip','Cold War from 1947-1991 v0.51.zip','Nitrogen_Gunpack_0925.zip','The Division pack_ver.0.3.3.zip','[TaCZ]Warzone Ver1.1.7B.zip','mw2019.zip','mwIII_attachments0.1.5are2.zip','throwable_thing_v1.4.0-1.1.5.zip']
seen={};report=[]
for name in selected:
 p=source/name
 with zipfile.ZipFile(p) as pack:
  assert pack.testzip() is None
  data=[n for n in pack.namelist() if n.startswith('data/') and n.endswith('.json')]
  conflicts=[n for n in data if n in seen and seen[n]!=hashlib.sha256(pack.read(n)).hexdigest()]
  if conflicts:report.append({'pack':name,'excluded_conflicts':conflicts});continue
  for n in data:seen[n]=hashlib.sha256(pack.read(n)).hexdigest()
  shutil.copy2(p,target/name);report.append({'pack':name,'included':True,'data_files':len(data),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
write(P/'gunpack-audit.json',report)
print('Skills:',len(skills),'Apotheosis resources:',len(changes),'Gunpacks:',sum(x.get('included',False) for x in report))
