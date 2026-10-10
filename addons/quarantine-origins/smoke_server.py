from pathlib import Path
import subprocess,time,threading,queue,sys
P=Path(__file__).resolve().parent;(P/'run').mkdir(exist_ok=True);(P/'run/eula.txt').write_text('eula=true\n');(P/'run/server.properties').write_text('online-mode=false\nlevel-type=minecraft:flat\nview-distance=2\nsimulation-distance=2\n')
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
   ready=True;p.stdin.write('stop\n');p.stdin.flush()
 if p.poll() is None:
  try:p.wait(timeout=35)
  except subprocess.TimeoutExpired:p.kill();p.wait()
print('SERVER_READY',ready,'EXIT',p.returncode)
sys.exit(0 if ready and p.returncode==0 else 1)
