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

write(root / 'pack.mcmeta', {'pack': {'pack_format': 48, 'description': 'Crafting Mastery: 31 skills'}})
write(base / 'config.json', {'version': 3, 'categories': ['crafting']})
write(category / 'category.json', {
    'title': 'Мастерство крафта',
    'description': 'Опыт за крафт. Навыки навсегда улучшают только новые изделия.',
    'icon': icon('crafting_table'),
    'background': 'minecraft:textures/gui/advancements/backgrounds/adventure.png',
    'unlocked_by_default': True, 'starting_points': 0,
})
definitions = {'root': {'title': 'Начинающий мастер', 'description': 'Открывает три ветки мастерства.',
                       'icon': icon('crafting_table'), 'cost': 1, 'rewards': []}}
skills = {'root': {'x': 0, 'y': 0, 'definition': 'root', 'root': True}}
edges = []
for branch, name, item, x, description in [
    ('weapon', 'Оружейник', 'iron_sword', -120, '+3% к базовому бонусу урона нового оружия за ступень (до +30%).'),
    ('tool', 'Инструментальщик', 'iron_pickaxe', 0, '+5% к скорости добычи новых инструментов за ступень (до +50%).'),
    ('armor', 'Бронник', 'iron_chestplate', 120, '+3% к базовой защите новой брони за ступень (до +30%).'),
]:
    for level in range(1, 11):
        key = f'{branch}_{level}'
        definitions[key] = {'title': f'{name} {level}/10', 'description': description + ' Старые предметы не меняются.',
                            'icon': icon(item), 'cost': 1, 'rewards': []}
        skills[key] = {'x': x, 'y': level * 48, 'definition': key}
        edges.append(['root' if level == 1 else f'{branch}_{level-1}', key])
write(category / 'definitions.json', definitions)
write(category / 'skills.json', skills)
write(category / 'connections.json', {'normal': {'bidirectional': edges}})
write(category / 'experience.json', {
    'level_limit': 50,
    'experience_per_level': {'type': 'expression', 'data': {'expression': '10 + level * 5'}},
    'sources': [{'type': 'puffish_skills:craft_item', 'data': {'variables': {}, 'experience': '1'}}],
})
assert len(skills) == 31 and len(edges) == 30
