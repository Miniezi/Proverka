"""Reproducible partial NeoForge migration, not a playable release."""
from pathlib import Path
import urllib.request,zipfile,hashlib,re,json,subprocess,shutil
P=Path(__file__).resolve().parent
SHA='215e687e687c4fa2a6a3db0237562d15eefed4c9'
ROOT=P/'work';ROOT.mkdir(exist_ok=True)
archive=ROOT/'tconstruct-upstream.zip'
if not archive.exists():urllib.request.urlretrieve('https://codeload.github.com/SlimeKnights/TinkersConstruct/zip/'+SHA,archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='49ddc838f002168dec6cb25e519937ade49a58e15dcefa47e20acb8b4925d941'
source=ROOT/('TinkersConstruct-'+SHA)
if source.exists():shutil.rmtree(source)
zipfile.ZipFile(archive).extractall(ROOT)
subprocess.run(['git','apply','--check',str(P/'resource-location.patch')],cwd=source,check=True)
subprocess.run(['git','apply',str(P/'resource-location.patch')],cwd=source,check=True)
from migrate_neoforge_api import migrate
counts={}
replacements={
 'net.minecraftforge.api.':'net.neoforged.api.',
 'net.minecraftforge.eventbus.':'net.neoforged.bus.',
 'net.minecraftforge.fml.':'net.neoforged.fml.',
 'net.minecraftforge.':'net.neoforged.neoforge.',
 'MinecraftForge':'NeoForge',
 'ForgeConfigSpec':'ModConfigSpec',
 'net.neoforged.fml.common.Mod.EventBusSubscriber':'net.neoforged.fml.common.EventBusSubscriber',
}
for f in source.rglob('*.java'):
 before=f.read_text();s=before
 for old,new in replacements.items():
  counts[old]=counts.get(old,0)+s.count(old);s=s.replace(old,new)
 s=re.sub(r'(?<![\w.])Mod\.EventBusSubscriber', 'net.neoforged.fml.common.EventBusSubscriber', s)
 if s!=before:f.write_text(s)
api_stats=migrate(source)
from migrate_registration import migrate as migrate_registration
api_stats["registration_files"] = migrate_registration(source)
from migrate_potions import migrate as migrate_potions
migrate_potions(source)
from migrate_attributes import migrate as migrate_attributes
migrate_attributes(source)
from migrate_holder_types import migrate as migrate_holder_types
api_stats["holder_types"] = migrate_holder_types(source)
from migrate_recipe_inputs import migrate as migrate_recipe_inputs
api_stats["recipe_input_files"] = migrate_recipe_inputs(source)
from migrate_crafting import migrate as migrate_crafting
api_stats["crafting_files"] = migrate_crafting(source)
from migrate_ticks import migrate as migrate_ticks
migrate_ticks(source)
from migrate_entity_data import migrate as migrate_entity_data
api_stats["entity_data_files"] = migrate_entity_data(source)
(ROOT/'api-migration-stats.json').write_text(json.dumps(api_stats,indent=2))
shutil.copyfile(P/'tconstruct.build.gradle',source/'build.gradle')
(source/'settings.gradle').write_text("pluginManagement { repositories { gradlePluginPortal(); maven { url='https://maven.neoforged.net/releases' } } }\nrootProject.name='TConstructNeoForgePort'\n")
(source/'gradle.properties').write_text('org.gradle.jvmargs=-Xmx4G\norg.gradle.daemon=false\n')
# Old SRG access transformers are retained as a migration input, not applied to Mojang names.
# The first compile inventories access errors alongside API errors; no fake stubs/excluded modules.
p=source/'src/main/resources/META-INF/mods.toml';s=p.read_text().replace('modId="forge"','modId="neoforge"').replace('mandatory=true','type="required"').replace('mandatory=false','type="optional"')
values={'loader_range':'[4,)','version':'3.12.1-port.dev','forge_range':'[21.1.238,)','minecraft_range':'[1.21.1,1.21.2)','mantle_range':'[1.12,)','jei_range':'[19,)','json_things_range':'*'}
for key,value in values.items():s=s.replace('${'+key+'}',value)
s=s.replace('    modId="tconstruct"','    modId="tconstruct"\n    enumExtensions="META-INF/enumextensions.json"')
p.with_name('neoforge.mods.toml').write_text(s);p.unlink()
for override in (P/'overrides').rglob('*'):
 if override.is_file():
  target=source/override.relative_to(P/'overrides');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(override,target)
(ROOT/'migration-stats.json').write_text(json.dumps({'upstream':SHA,'resource_location_calls':116,'replacements':counts,'java_files':len(list(source.rglob('*.java')))},indent=2))
# Fail preparation if a rename accidentally changes a project-owned public type.
for java in (source/'src/main/java').rglob('*.java'):
 for name in re.findall(r'^public\s+(?:(?:abstract|final|sealed)\s+)*(?:class|interface|enum|record)\s+(\w+)', java.read_text(), re.M):
  if name != java.stem:
   raise RuntimeError(f"Public type {name} no longer matches {java}")
print(source)
