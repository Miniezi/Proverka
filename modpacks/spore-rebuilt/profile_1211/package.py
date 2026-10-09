from pathlib import Path
import json,zipfile,hashlib,shutil,tomllib
P=Path(__file__).resolve().parent;O=P/'overrides';OUT=P/'output';OUT.mkdir(exist_ok=True)
d=json.loads((P/'modrinth-candidate.json').read_text());files=[];seen=set()
for v in d['versions']:
 assert v['project_id'] not in seen,'duplicate project';seen.add(v['project_id'])
 assert '1.21.1' in v['game_versions'] and 'neoforge' in v['loaders']
 f=next((x for x in v['files'] if x['primary']),v['files'][0]);p=P/'mods'/f['filename'];b=p.read_bytes()
 assert len(b)==f['size']
 for alg,h in f['hashes'].items():assert hashlib.new(alg,b).hexdigest()==h
 files.append({'path':'mods/'+f['filename'],'hashes':f['hashes'],'downloads':[f['url']],'fileSize':f['size'],'env':{'client':'required','server':'required'}})
# The compatibility fix is newer on CurseForge; include its unmodified GPL jar.
extras=json.loads((P/'external-files.json').read_text())
for f in extras:
 b=(P/f['path']).read_bytes()
 for alg,h in f['hashes'].items():assert hashlib.new(alg,b).hexdigest()==h
 dst=O/f['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/f['path'],dst)
index={'formatVersion':1,'game':'minecraft','versionId':'0.1.0-rc1','name':'Quarantine: Spore Arsenal','summary':'NeoForge 1.21.1 — Spore, TaCZ, technology, 60 skills, Apotheosis rebalance. Server-tested release candidate.','dependencies':{'minecraft':'1.21.1','neoforge':json.loads((P/'loader.json').read_text())['neoforge']},'files':files}
(P/'modrinth.index.json').write_text(json.dumps(index,indent=2)+'\n')
lines=['# Моды — Quarantine RC1','', 'Файлы закреплены; не обновляйте отдельные моды без повторной проверки.','']
lines += [f"- {v['name']} — https://modrinth.com/mod/{v['project_id']}/version/{v['id']}" for v in d['versions']]
lines += ['- MCA / Easy Villagers Compat: файл 9029813, mca-ev-compat-1.21.1-2.2.7.jar — https://www.curseforge.com/minecraft/mc-mods/mca-reborn-x-easy-villagers-compat/files/9029813','', 'Авторство и лицензии исходных модов и паков принадлежат их авторам. Оружейные архивы взяты из предоставленного пользователем профиля, исправленные копии предназначены для его использования.']
(O/'MODS_RU.md').write_text('\n'.join(lines)+'\n')
readme='''# Quarantine: Spore Arsenal — 1.21.1 NeoForge / RC1

Импортируйте файл .mrpack в лаунчер с поддержкой Modrinth-пакетов. Не кладите его в папку mods. Нужны Java 21 и интернет для загрузки модов по манифесту. Для компьютера с 16 ГБ ОЗУ начните с выделения игре 6–8 ГБ. Создайте НОВЫЙ мир, сложность «Сложная». Старую карту 1.20.1 сюда не переносите.

## Состав
38 JAR: Spore 2.2.0j, TaCZ 1.1.8-hotfix-r7, Mekanism + Generators + Tools, Immersive Engineering, Apotheosis, Pufferfish Skills/Attributes, Just Hammers, MCA Reborn + Easy Villagers + исправленный compat-аддон, JEI, Jade, рюкзаки и хранилища, Waystones, данжи YUNG's, When Dungeons Arise, Dungeons and Taverns. Create отсутствует. Загрузчик NeoForge 21.1.256 установлен манифестом.

Пять дополнительных паков TaCZ: Apocalypse, ChocolateMan, The Division, MW2019, Throwable Thing. В личных копиях удалены сломанные индексы JAK12/одного штыка и неподдерживаемые блоки-техника Apocalypse; поправлена ссылка на стандартный скрипт MW2019. Остальное оружие сохранено. Nitrogen несовместим с текущим форматом и исключён. Базовый арсенал TaCZ также доступен. Рецепты смотрите в JEI и оружейных верстаках.

## Прогрессия и баланс
- Меню навыков: K. 60 узлов, шесть веток по 10: здоровье, броня, скорость, ближний бой, скорость атаки, сопротивление отбрасыванию. Одно стартовое очко, остальные за бои; стоимость уровней растёт. Навыки усиливают персонажа, не добавляют старый отдельный аддон крафтовых характеристик.
- Spore: обычная эволюция 600 секунд / от 2 убийств, гиперэволюция 1200 секунд / от 9 убийств. Сохранена собственная прогрессия инфекции. Это не сценарий фиксированных стадий по дням.
- Лимиты заражённых снижены с 60/35/20/40/30 до 45/24/12/24/16. Загрузка чанков каламити отключена. Здоровье инфекции ×1.15, урон ×1.10.
- Числовые атрибуты аффиксов и камней Apotheosis уменьшены примерно на 35%; уровни мира и условия доступа Apotheosis сохранены. Специальные эффекты отдельно не урезаны. Добавлены четыре типа заражённых Spore в таблицы вторжений Apotheosis; крупные каламити не превращаются в случайных боссов.
- FerriteCore, ModernFix и Lithium используются для снижения нагрузки. Chunky включён, но автоматическая генерация большой карты не запускается. Оптимизация не гарантирует отсутствие фризов на любом оборудовании.

## Проверка и ограничения
Сервер с этим набором запускается, создаёт/загружает мир, загружает навыки и завершает работу с сохранением. Клиентский рендер оружия, вход реального игрока, интерфейсы MCA и длительная прогрессия ещё не проверены. Это кандидат RC1, а не обещание полной совместимости и окончательного игрового баланса.
Остаются четыре пропущенных достижения исходных модов данжей; на запуск мира они не повлияли. Сетевое предупреждение получения ключа Mojang возникло в тестовом окружении, а не из-за изменений сборки.

Если игра упадёт, пришлите logs/latest.log и последний файл из crash-reports. Не добавляйте другие версии MCA или compat поверх установленных.
'''
(O/'README_RU.md').write_text(readme)
# Validate nested gun archives as well as the outer installer.
for gp in (O/'tacz').glob('*.zip'):
 with zipfile.ZipFile(gp) as z:assert z.testzip() is None
# Do not ship test-world files, Java, credentials, caches, or downloaded mod copies.
archive=OUT/'Quarantine-Spore-Arsenal-1.21.1-RC1.mrpack'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('modrinth.index.json',json.dumps(index,indent=2))
 for p in sorted(O.rglob('*')):
  if p.is_file():z.write(p,'overrides/'+p.relative_to(O).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(archive,archive.stat().st_size,'bytes;',len(files)+len(extras),'mod jars;',len(list((O/'tacz').glob('*.zip'))),'gunpacks')
