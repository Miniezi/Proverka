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
valid=all(marker in contents for marker in ['TCONSTRUCT_TYPED_IDS_OK equality=1 hashing=1 validation=1 parsing=1 wire=1', 'TCONSTRUCT_NETWORK_CORE_OK item_components=1 empty_items=1 fluid=1 empty_fluid=1', 'TCONSTRUCT_WORLD_PACKETS_OK codecs=2 movement=1 missing_entity=1 immutable_position=1', 'TCONSTRUCT_PERSISTENT_PACKET_OK roundtrip=1 snapshot=1 replace=1 empty=1 identity=1', 'TCONSTRUCT_PERSISTENT_DATA_OK save_load=1 death_copy=1 return_copy=1 deep_copy=1 empty_omitted=1', 'TCONSTRUCT_DISPLAY_MIGRATION_OK contexts=6 unique_ids=6 fallbacks=6', 'TCONSTRUCT_CAST_MIGRATION_OK constructors=2 variants=3 tags=2', 'TCONSTRUCT_POTION_MIGRATION_OK effects=5 containers=3 rebuilds=2 mixes=30', 'TCONSTRUCT_EFFECT_MIGRATION_OK operations=2 removal=2 no_duplicate_modifiers=1', 'TCONSTRUCT_RECIPE_INPUT_OK single=1 casting=1 molding_slots=2 fluid=1 live_views=1', 'TCONSTRUCT_CRAFTING_OK shifted_shape=1 remainder_offset=1 smelting=1 no_mutation=1', 'TCONSTRUCT_ENTITY_DATA_OK lazy=1 isolated=1 transient=1 computed=1 stable_identity=1'])
print('DATA_VALID',valid)
print('SERVER_READY',ready,'EXIT',p.returncode)
sys.exit(0 if ready and valid and p.returncode==0 else 1)
