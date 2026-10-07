"""Deterministically generate the bundled crafting tree."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'datapack'
base = root / 'data/crafter/puffish_skills'
category = base / 'categories/crafting'
category.mkdir(parents=True, exist_ok=True)
def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def icon(item):
    return {'type': 'item', 'data': {'item': 'minecraft:' + item}}

write(root / 'pack.mcmeta', {'pack': {'pack_format': 48, 'description': 'Crafting Mastery: 64 skills'}})
write(base / 'config.json', {'version': 3, 'categories': ['crafting']})
write(category / 'category.json', {
    'title': 'Мастерство крафта',
    'description': '64 узла: корень, три ветки по 20 ступеней и три особых навыка. Обычный бонус до +30%; особый навык даёт шанс 5% дополнительно усилить характеристику на 50%.',
    'icon': icon('crafting_table'),
    'background': 'minecraft:textures/gui/advancements/backgrounds/adventure.png',
    'unlocked_by_default': True, 'starting_points': 0,
})
definitions = {'root': {'title': 'Начинающий мастер', 'description': 'Открывает все три ветки. Цена: 1 очко. Создавайте предметы, получайте опыт и выбирайте улучшения. Уже имеющиеся предметы не меняются.',
                       'icon': icon('crafting_table'), 'cost': 1, 'rewards': []}}
skills = {'root': {'x': 0, 'y': 0, 'definition': 'root', 'root': True}}
edges = []
for branch, name, item, x, step, stat in [
    ('weapon', 'Оружейник', 'sword', -120, 1.5, 'базовому бонусу урона нового оружия'),
    ('tool', 'Инструментальщик', 'pickaxe', 0, 1.5, 'скорости добычи нового инструмента'),
    ('armor', 'Бронник', 'chestplate', 120, 1.5, 'базовой защите новой брони'),
]:
    for level in range(1, 21):
        key = f'{branch}_{level}'
        material = 'iron' if level <= 7 else 'diamond' if level <= 14 else 'netherite'
        description = (f'Эта ступень: +{step}%. Итого после открытия: +{step * level}% к {stat} и максимальной прочности подходящего предмета. '
                       'Цена: 1 очко. Бонус получает только новое изделие; старые предметы не меняются. '
                       'Бонус сохраняется при передаче предмета и сбросе навыков.')
        definitions[key] = {'title': f'{name} {level}/20', 'description': description,
                            'icon': icon(material + '_' + item), 'cost': 1, 'rewards': []}
        skills[key] = {'x': x, 'y': level * 48, 'definition': key}
        edges.append(['root' if level == 1 else f'{branch}_{level-1}', key])
    key = branch + '_master'
    definitions[key] = {'title': name + ': шедевр', 'cost': 1, 'icon': icon('netherite_' + item),
        'description': 'При получении нового изделия: отдельный шанс 5% умножить характеристику и максимальную прочность этой ветки на 1,5. '
                       'С обычным бонусом +30% итог равен +95% к исходной характеристике и прочности. '
                       'Проверки урона, добычи и защиты независимы. Старые предметы не меняются.', 'rewards': []}
    skills[key] = {'x': x, 'y': 21 * 48, 'definition': key}
    edges.append([branch + '_20', key])
write(category / 'definitions.json', definitions)
write(category / 'skills.json', skills)
write(category / 'connections.json', {'normal': {'unidirectional': edges}})
write(category / 'experience.json', {
    'level_limit': 64,
    'experience_per_level': {'type': 'expression', 'data': {'expression': '10 + level * 5'}},
    'sources': [{'type': 'puffish_skills:craft_item', 'data': {'variables': {}, 'experience': '1'}}],
})
assert len(skills) == 64 and len(edges) == 63
