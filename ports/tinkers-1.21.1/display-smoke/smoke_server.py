from pathlib import Path
import subprocess,time,threading,queue,sys
P=Path(__file__).resolve().parent;(P/'run').mkdir(exist_ok=True);(P/'run/eula.txt').write_text('eula=true\n');(P/'run/server.properties').write_text('online-mode=false\nlevel-type=minecraft:flat\nview-distance=2\nsimulation-distance=2\ngenerator-settings={"layers":[{"block":"minecraft:bedrock","height":1},{"block":"minecraft:dirt","height":2},{"block":"minecraft:grass_block","height":1}],"biome":"minecraft:plains"}\n')
p=subprocess.Popen(['gradle','runServer','--no-daemon','--console=plain'],cwd=P,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
q=queue.Queue()
def read():
 for line in p.stdout:q.put(line)
threading.Thread(target=read,daemon=True).start();deadline=time.time()+420;ready=False
with (P/'server-smoke.log').open('w') as log:
 while time.time()<deadline:
  try:line=q.get(timeout=1)
  except queue.Empty:
   if p.poll() is not None:break
   continue
  log.write(line);log.flush()
  if 'Done (' in line and not ready:
   ready=True
   try:p.stdin.write('stop\n');p.stdin.flush()
   except BrokenPipeError:pass
 if p.poll() is None:
  try:p.wait(timeout=35)
  except subprocess.TimeoutExpired:p.kill();p.wait()
contents=(P/'server-smoke.log').read_text()
valid=all(marker in contents for marker in ['TCONSTRUCT_SMELTERY_FUEL_OK datapack=1 json=1 wire=1 reload=1 liquid=1 solid=1 persistence=1', 'TCONSTRUCT_SMELTERY_CAPABILITIES_OK registration=1 sides=1 invalidation=1 replacement=1 forwarding=1 conservation=1 filters=1 positions=1', 'TCONSTRUCT_CASTING_TANK_OK simulation=1 transfer=1 components=1 persistence=1 reset=1', 'TCONSTRUCT_RECIPE_ID_CACHE_OK lookup=1 replacement=1 removal=1', 'TCONSTRUCT_DISPENSER_OK placement=1 consumption=1 blocked=1 components=1', 'TCONSTRUCT_GLASS_BLOCKS_OK colors=16 codecs=5 culling=1 soul=1', 'TCONSTRUCT_RESTRICTED_DATA_OK protection=1 isolation=1 publication=1 atomic=1', 'TCONSTRUCT_CROSSBOW_ATTRIBUTION_OK vanilla=1 tagged=1 exclusions=1 persistence=1', 'TCONSTRUCT_PROJECTILE_AIM_OK direction=1 spread=1 target=1 arrow=1', 'TCONSTRUCT_STORED_ITEMS_OK components=1 enchantments=1 isolation=1 invalid=1', 'TCONSTRUCT_TOOL_INVENTORY_OK edits=1 isolation=1 relocation=1 rejection=1', 'TCONSTRUCT_MODIFIER_DATA_OK snapshots=1 self_copy=1 nested=1 atomic=1', 'TCONSTRUCT_ITEM_DATA_OK isolation=1 atomic=1 preservation=1 persistence=1 wire=1', 'TCONSTRUCT_CUSTOM_INGREDIENTS_OK registration=1 containers=1 nested_components=1 json=1 wire=1 ranges=1', 'TCONSTRUCT_MATERIAL_PATTERN_OK identity=1 repeated_parts=1 shape=1 json=1 wire=1 rejection=1', 'TCONSTRUCT_INGREDIENTS_OK quantity=1 alternatives=1 tags=1 json=1 wire=1', 'TCONSTRUCT_TYPED_IDS_OK equality=1 hashing=1 validation=1 parsing=1 wire=1', 'TCONSTRUCT_NETWORK_CORE_OK item_components=1 empty_items=1 fluid=1 empty_fluid=1', 'TCONSTRUCT_WORLD_PACKETS_OK codecs=2 movement=1 missing_entity=1 immutable_position=1', 'TCONSTRUCT_PERSISTENT_PACKET_OK roundtrip=1 snapshot=1 replace=1 empty=1 identity=1', 'TCONSTRUCT_PERSISTENT_DATA_OK save_load=1 death_copy=1 return_copy=1 deep_copy=1 empty_omitted=1', 'TCONSTRUCT_DISPLAY_MIGRATION_OK contexts=6 unique_ids=6 fallbacks=6', 'TCONSTRUCT_CAST_MIGRATION_OK constructors=2 variants=3 tags=2', 'TCONSTRUCT_POTION_MIGRATION_OK effects=5 containers=3 rebuilds=2 mixes=30', 'TCONSTRUCT_EFFECT_MIGRATION_OK operations=2 removal=2 no_duplicate_modifiers=1', 'TCONSTRUCT_RECIPE_INPUT_OK single=1 casting=1 molding_slots=2 fluid=1 live_views=1', 'TCONSTRUCT_CRAFTING_OK shifted_shape=1 remainder_offset=1 smelting=1 no_mutation=1', 'TCONSTRUCT_ENTITY_DATA_OK lazy=1 isolated=1 transient=1 computed=1 stable_identity=1'])
print('DATA_VALID',valid)
print('SERVER_READY',ready,'EXIT',p.returncode)
sys.exit(0 if ready and valid and p.returncode==0 else 1)
