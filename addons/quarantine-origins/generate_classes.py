from pathlib import Path
import json
P=Path(__file__).resolve().parent/'src/main/resources'
def write(path,data):
 f=P/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def power(id,name,description,typ,**fields):
 write('data/quarantine/origins/powers/'+id+'.json',dict(type='neoorigins:'+typ,name={'text':name},description={'text':description},**fields));return 'quarantine:'+id
def attr(id,name,desc,attribute,amount,operation='add_value'):
 return power(id,name,desc,'attribute_modifier',attribute=attribute,amount=amount,operation=operation)
def dmg(id,name,desc,multiplier,damage_type=None):
 return power(id,name,desc,'modify_damage',direction='in',multiplier=multiplier,**({'damage_type':damage_type} if damage_type else {}))
classes=[]
def origin(id,name,desc,icon,powers,impact='medium'):
 classes.append('quarantine:'+id);write('data/quarantine/origins/origins/'+id+'.json',dict(name={'text':name},description={'text':desc},icon=icon,impact=impact,order=len(classes),powers=powers))
origin('survivor','Выживший','Обычный человек. Без врождённых бонусов и штрафов; развитие через снаряжение и древо навыков.','minecraft:bread',[], 'none')
origin('infected','Носитель мицелия','Симбиоз I постоянно поддерживается. Обычные заражённые Spore замечают тебя только в радиусе 8 блоков, пока бой не начался. Эволюции, каламити и существа с более чем 80 HP не обманываются. Удар по заражённому раскрывает тебя. +4 сердца, но -10% скорости.\nКриогенный аппарат вызывает обморожение даже без грибной брони. 10 секунд на открытом морозе, в холодной воде или рыхлом снегу тоже вызывают обморожение. Оно замедляет и наносит 2–6 урона каждые 4 секунды; маскировка пропадает. Крыша защищает от холодного воздуха, огнестойкость — от накопления холода. Симбиоз расходует сытость по правилам Spore.','minecraft:red_mushroom',[
 attr('infected_health','Разросшийся мицелий','+8 здоровья (4 сердца).','minecraft:generic.max_health',8),
 attr('infected_speed','Тяжёлая биомасса','-10% скорости передвижения.','minecraft:generic.movement_speed',-.1,'add_multiplied_base')], 'high')
origin('cryogenic','Криостазник','Адаптирован к криогенной обработке: иммунитет к обморожению Spore, вдвое меньше урона замерзания. Хрупкие ткани: -1 сердце и +35% урона огня.','minecraft:blue_ice',[
 power('cryo_immunity','Холодная кровь','Обморожение Spore не применяется.','effect_immunity',effects=['spore:frostbite']),
 dmg('cryo_freeze','Криоадаптация','Вдвое меньше урона замерзания.',.5,'freeze'),
 dmg('cryo_fire','Термошок','На 35% больше урона огня.',1.35,'#minecraft:is_fire'),
 attr('cryo_health','Цена криостаза','-2 здоровья.','minecraft:generic.max_health',-2)])
origin('engineer','Монтажник убежища','Обслуживает Mekanism и Immersive Engineering: +0.75 блока взаимодействия, +15% скорости добычи и +1 твёрдости брони. -15% базового урона ближнего боя. Машины сами по себе быстрее не работают.','minecraft:repeater',[
 attr('engineer_reach','Монтажная хватка','+0.75 блока взаимодействия с блоками.','minecraft:player.block_interaction_range',.75),
 attr('engineer_mining','Быстрый демонтаж','+15% скорости добычи.','apothic_attributes:mining_speed',.15,'add_multiplied_base'),
 attr('engineer_toughness','Рабочая защита','+1 твёрдости брони.','minecraft:generic.armor_toughness',1),
 attr('engineer_melee','Не боец','-15% базового урона ближнего боя.','minecraft:generic.attack_damage',-.15,'add_multiplied_base')])
origin('gunner','Стрелок периметра','+12% урона снарядов, включая пули TaCZ. Цена специализации: -1 сердце и -15% базового урона ближнего боя. Бонус не меняет отдачу, магазин или перезарядку.','minecraft:crossbow',[
 attr('gunner_damage','Пристрелянное оружие','+12% урона снарядов.','apothic_attributes:projectile_damage',.12,'add_multiplied_base'),
 attr('gunner_health','Лёгкое снаряжение','-2 здоровья.','minecraft:generic.max_health',-2),
 attr('gunner_melee','Держи дистанцию','-15% базового урона ближнего боя.','minecraft:generic.attack_damage',-.15,'add_multiplied_base')])
origin('scavenger','Ходок руин','Для вылазок в данжи: +10% скорости, +2 блока безопасного падения, +1 удачи. -2 сердца. Удача влияет только на таблицы добычи, которые её учитывают; она не гарантирует редкие камни Apotheosis.','minecraft:compass',[
 attr('scavenger_speed','Бег между укрытиями','+10% скорости.','minecraft:generic.movement_speed',.1,'add_multiplied_base'),
 attr('scavenger_fall','Опыт высотных вылазок','+2 блока безопасного падения.','minecraft:generic.safe_fall_distance',2),
 attr('scavenger_luck','Поиск припасов','+1 удачи.','minecraft:generic.luck',1),
 attr('scavenger_health','Хрупкость','-4 здоровья.','minecraft:generic.max_health',-4)])
origin('medic','Полевой биолог','+25% получаемого лечения, +1 сердце и иммунитет к обычному яду. Не защищает от заражения Spore и не лечит союзников автоматически. -15% базового урона ближнего боя и -10% урона снарядов.','minecraft:golden_apple',[
 attr('medic_heal','Усвоение препаратов','+25% получаемого лечения.','apothic_attributes:healing_received',.25,'add_multiplied_base'),
 attr('medic_health','Медицинская подготовка','+2 здоровья.','minecraft:generic.max_health',2),
 power('medic_poison','Антитоксины','Иммунитет только к обычному яду.','effect_immunity',effects=['minecraft:poison']),
 attr('medic_melee','Врач, а не штурмовик','-15% базового урона ближнего боя.','minecraft:generic.attack_damage',-.15,'add_multiplied_base'),
 attr('medic_projectile','Ограниченная огневая подготовка','-10% урона снарядов.','apothic_attributes:projectile_damage',-.1,'add_multiplied_base')])
write('data/neoorigins/origins/origin_layers/class.json',{'replace':True,'name':{'text':'Карантин: классы'},'order':1,'origins':classes,'enabled':True,'hidden':False,'allow_random':False})
write('data/neoorigins/origins/origin_layers/origin.json',{'replace':True,'enabled':False,'origins':[]})
write('pack.mcmeta',{'pack':{'pack_format':48,'description':'Quarantine classes for NeoOrigins 2.2.29 / MC 1.21.1'}})
assert len(classes)==7
for f in (P/'data/quarantine/origins/origins').glob('*.json'):
 for id in json.loads(f.read_text())['powers']:assert (P/('data/quarantine/origins/powers/'+id.split(':')[1]+'.json')).exists()
print('7 classes,',len(list((P/'data/quarantine/origins/powers').glob('*.json'))),'powers; references checked')
