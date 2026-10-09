from pathlib import Path
import json,math,shutil,zipfile
P=Path(__file__).resolve().parent;O=P/'overrides';S=O/'config/puffish_skills';C=S/'categories/quarantine';D=O/'config/paxi/datapacks/quarantine_skills'
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def reward(a,v,op='addition'):return {'type':'puffish_skills:attribute','data':{'attribute':a,'value':v,'operation':op}}
# Each branch has five tiers: a trunk skill and two optional side skills per tier.
# Each next trunk depends only on the preceding trunk; specialists pay for side skills separately.
branches=[
 {'id':'marksman','name':'Стрелок','icon':'tacz:modern_kinetic_gun','names':['Контроль огня','Дальний патруль','Охотник на мутантов','Огневая поддержка','Последний рубеж'],
 'main':('apothic_attributes:projectile_damage',.03,'multiply_base','+3% урона снарядов, включая пули TaCZ'),
 'left':('minecraft:generic.movement_speed',.01,'multiply_base','Смена позиции: +1% скорости передвижения'),
 'right':('minecraft:generic.knockback_resistance',.02,'addition','Устойчивая стойка: +2 п.п. сопротивления отбрасыванию (не отдаче оружия)'),
 'cap':('Снайпер карантина',[reward('apothic_attributes:projectile_damage',.05,'multiply_base')],'+5% урона снарядов. Вместе со стволом ветки: +20%.')},
 {'id':'breacher','name':'Штурмовик','icon':'minecraft:iron_sword','names':['Зачистка коридоров','Работа клинком','Встречный удар','Прорыв оцепления','Бой с элитой'],
 'main':('minecraft:generic.attack_damage',.04,'multiply_base','+4% урона ближнего боя'),
 'left':('minecraft:generic.attack_speed',.02,'multiply_base','Темп боя: +2% скорости ближних атак'),
 'right':('minecraft:generic.armor',.4,'addition','Штурмовая защита: +0.4 брони'),
 'cap':('Пролом',[reward('minecraft:generic.attack_damage',.1,'multiply_base')],'+10% урона ближнего боя. Всего по основной линии: +30%.')},
 {'id':'engineer','name':'Инженер','icon':'mekanism:steel_casing','names':['Ремонтный участок','Монтажная бригада','Промышленная база','Силовая станция','Обслуживание комплекса'],
 'main':('minecraft:player.block_interaction_range',.1,'addition','+0.1 блока дальности взаимодействия с блоками'),
 'left':('apothic_attributes:mining_speed',.02,'multiply_base','Демонтаж: +2% скорости добычи'),
 'right':('minecraft:generic.armor_toughness',.2,'addition','Рабочая защита: +0.2 твёрдости брони'),
 'cap':('Главный механик',[reward('minecraft:player.block_interaction_range',.5)],'+0.5 блока дальности взаимодействия. Вместе с основной линией: +1 блок. Не ускоряет тики машин.')},
 {'id':'miner','name':'Старатель','icon':'minecraft:diamond_pickaxe','names':['Разведка залежей','Проходка шахты','Промышленный забой','Глубинная выработка','Ресурсный резерв'],
 'main':('apothic_attributes:mining_speed',.04,'multiply_base','+4% скорости добычи блоков'),
 'left':('minecraft:generic.max_health',.4,'addition','Шахтёрская выносливость: +0.4 здоровья'),
 'right':('minecraft:generic.safe_fall_distance',.2,'addition','Страховка: +0.2 блока безопасного падения'),
 'cap':('Мастер проходки',[reward('apothic_attributes:mining_speed',.1,'multiply_base')],'+10% скорости добычи. Всего в этой ветке: +30%. Бонус персонажа; работу области 3×3 определяет Just Hammers.')},
 {'id':'medic','name':'Полевой медик','icon':'minecraft:golden_apple','names':['Первая помощь','Перевязочный пункт','Полевой лазарет','Эвакуация раненых','Медицинский резерв'],
 'main':('apothic_attributes:healing_received',.04,'multiply_base','+4% получаемого лечения'),
 'left':('minecraft:generic.max_health',.6,'addition','Запас сил: +0.6 здоровья'),
 'right':('minecraft:generic.armor',.2,'addition','Защитное снаряжение: +0.2 брони'),
 'cap':('Реаниматор',[reward('apothic_attributes:healing_received',.1,'multiply_base'),reward('minecraft:generic.max_health',1)],'+10% получаемого лечения и +1 здоровья. Не даёт иммунитета к Spore и не лечит заражение автоматически.')},
 {'id':'scout','name':'Разведчик','icon':'minecraft:compass','names':['Маршрут отхода','Обход заражения','Рейд за припасами','Разведка данжей','Глубокий рейд'],
 'main':('minecraft:generic.movement_speed',.015,'multiply_base','+1.5% скорости передвижения'),
 'left':('minecraft:generic.safe_fall_distance',.3,'addition','Безопасный спуск: +0.3 блока безопасного падения'),
 'right':('minecraft:generic.max_health',.4,'addition','Походная выносливость: +0.4 здоровья'),
 'cap':('Следопыт',[reward('minecraft:generic.movement_speed',.025,'multiply_base'),reward('minecraft:generic.safe_fall_distance',.5)],'+2.5% скорости и +0.5 блока безопасного падения. Основная линия скорости суммарно +10%.')}
]
write(S/'config.json',{'version':3,'show_warnings':True,'categories':['quarantine']})
write(C/'category.json',{'title':'Карантин: специализации','description':'97 навыков, до 70 очков. Бои с заражёнными, вылазки и технические крафты. Все ветви доступны; полностью изучить всё нельзя.','unlocked_by_default':True,'exclusive_root':False,'starting_points':1,'spent_points_limit':70,'icon':{'type':'item','data':{'item':'minecraft:recovery_compass'}},'background':'minecraft:textures/gui/advancements/backgrounds/deepslate.png'})
defs={};skills={};links=[];summary=[]
def node(sid,title,desc,item,rewards,x,y,cost=1,root=False,frame='task',spent=0):
 defs[sid]={'title':title,'description':desc,'icon':{'type':'item','data':{'item':item}},'frame':{'type':'advancement','data':{'frame':frame}},'cost':cost,'required_spent_points':spent,'rewards':rewards}
 skills[sid]={'x':round(x),'y':round(y),'definition':sid,'root':root}
node('quarantine_induction','Допуск в зону','Начало подготовки. Открывает шесть направлений; можно сочетать специализации.','minecraft:recovery_compass',[],0,0,root=True,frame='challenge')
for bi,b in enumerate(branches):
 angle=bi*math.pi/3-math.pi/2;ux,uy=math.cos(angle),math.sin(angle);vx,vy=-uy,ux;previous='quarantine_induction'
 for tier in range(1,6):
  radius=100+tier*74;mx,my=ux*radius,uy*radius
  main=f"{b['id']}_core_{tier}"
  a,v,op,desc=b['main'];node(main,b['names'][tier-1],desc,b['icon'],[reward(a,v,op)],mx,my,spent=(tier-1)*3,frame='goal');links.append([previous,main]);previous=main
  for side,offset in [('left',-32),('right',32)]:
   a,v,op,desc=b[side];sid=f"{b['id']}_{side}_{tier}";node(sid,desc.split(':')[0]+f' {tier}',desc,b['icon'],[reward(a,v,op)],mx+vx*offset+ux*28,my+vy*offset+uy*28,spent=(tier-1)*3);links.append([main,sid])
 title,rs,desc=b['cap'];sid=b['id']+'_master';node(sid,title,desc,b['icon'],rs,ux*570,uy*570,cost=3,frame='challenge',spent=25);links.append([previous,sid])
 summary.append({'branch':b['name'],'nodes':16,'full_cost':18,'master':title,'master_description':desc})
write(C/'definitions.json',defs);write(C/'skills.json',skills);write(C/'connections.json',links)
write(D/'pack.mcmeta',{'pack':{'pack_format':48,'description':'Quarantine specialization XP tags'}})
# Only living infected IDs verified from this installed Spore's translations. Optional tag members handle future removals.
with zipfile.ZipFile(next((P/'mods').glob('spore*'))) as z:lang=json.loads(z.read('assets/spore/lang/en_us.json'))
spore=['spore:'+k.removeprefix('entity.spore.') for k in lang if k.startswith('entity.spore.')]
write(D/'data/quarantine/tags/entity_type/infected.json',{'replace':False,'values':[{'id':x,'required':False} for x in spore]})
crafts=['mekanism:steel_casing','mekanism:metallurgic_infuser','mekanism:enrichment_chamber','mekanism:crusher','mekanism:energized_smelter','mekanism:electrolytic_separator','mekanism:chemical_infuser','mekanism:chemical_injection_chamber','mekanism:purification_chamber','mekanismgenerators:heat_generator','mekanismgenerators:wind_generator','immersiveengineering:hammer','immersiveengineering:wirecutter','immersiveengineering:capacitor_lv','immersiveengineering:capacitor_mv','immersiveengineering:capacitor_hv','immersiveengineering:drill','immersiveengineering:chemthrower']
write(D/'data/quarantine/tags/item/technical_crafts.json',{'replace':False,'values':crafts})
kill={'type':'puffish_skills:kill_entity','data':{'variables':{'xp':{'operations':[{'type':'get_dropped_experience'}]},'infected':{'operations':[{'type':'get_killed_living_entity'},{'type':'get_type'},{'type':'puffish_skills:test','data':{'entity_type':'#quarantine:infected'}}]}},'experience':[{'condition':'infected','expression':'12 + min(xp, 28)'},{'condition':'!infected','expression':'min(xp, 15)'}],'anti_farming_per_chunk':{'limit_per_chunk':20,'reset_after_seconds':300}}}
craft={'type':'puffish_skills:craft_item','data':{'variables':{'technical':{'operations':[{'type':'get_crafted_item_stack'},{'type':'puffish_skills:test','data':{'item':'#quarantine:technical_crafts'}}]}},'experience':[{'condition':'technical','expression':'12'}]}}
write(C/'experience.json',{'level_limit':69,'experience_per_level':{'type':'expression','data':{'expression':'80 + level * 12'}},'sources':[kill,craft]})
# Old tree stays recoverable in RC1, but is not loaded or shipped with RC2.
if (S/'categories/survival').exists():shutil.rmtree(S/'categories/survival')
write(P/'CUSTOM_TREE_REPORT.json',{'nodes':len(skills),'connections':len(links),'max_points':70,'cost_to_unlock_everything':sum(d['cost'] for d in defs.values()),'branches':summary,'craft_items':crafts,'gun_compat_evidence':'TaCZ EntityKineticBullet extends Projectile; AttributeEvents.projDmg scales LivingIncomingDamageEvent for Projectile direct sources. Actual firing by a client is not tested.','stat_scope':'player attributes, not permanent crafted-item modifiers'})
assert len(skills)==97 and len(links)==96
# Verify graph reachability and non-overlapping positions.
assert len({(s['x'],s['y']) for s in skills.values()})==len(skills)
reachable={'quarantine_induction'}
while True:
 new=reachable|{b for a,b in links if a in reachable}|{a for a,b in links if b in reachable}
 if new==reachable:break
 reachable=new
assert len(reachable)==97
print('Created 97 connected skills; 6 branches; 70 spendable points; full tree costs',sum(d['cost'] for d in defs.values()))
