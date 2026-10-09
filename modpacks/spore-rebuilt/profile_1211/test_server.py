from pathlib import Path
import os,subprocess,json,shutil
p=Path(__file__).resolve().parent;s=p/'server';j=next((p/'runtime').glob('*/bin/java'));env=os.environ.copy();env['LD_LIBRARY_PATH']=str(j.parent.parent/'lib')+':'+str(j.parent.parent/'lib/server')
shutil.copytree(p/'mods',s/'mods',dirs_exist_ok=True)
if (p/'overrides').exists():shutil.copytree(p/'overrides',s,dirs_exist_ok=True)
(s/'eula.txt').write_text('eula=true\n');(s/'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25579\nview-distance=6\nsimulation-distance=4\ndifficulty=hard\nmax-players=2\nlevel-seed=73284591\n')
v=json.loads((p/'loader.json').read_text())['neoforge']
with (p/'server-test.log').open('w') as f:
 r=subprocess.Popen([str(j),f'-Djava.io.tmpdir={p / "tmp"}','-Xms512M','-Xmx4G',f'@libraries/net/neoforged/neoforge/{v}/unix_args.txt','nogui'],cwd=s,env=env,stdin=subprocess.PIPE,stdout=f,stderr=subprocess.STDOUT,text=True)
 (p/'server.pid').write_text(str(r.pid))
 import time
 for i in range(240):
  if r.poll() is not None:break
  time.sleep(1)
  if 'Done (' in (p/'server-test.log').read_text(errors='replace'):
   print('SERVER_READY',flush=True);r.stdin.write('stop\n');r.stdin.flush();r.wait(timeout=60);break
 else:r.terminate();r.wait(timeout=30)
 print('EXIT',r.returncode,flush=True)
