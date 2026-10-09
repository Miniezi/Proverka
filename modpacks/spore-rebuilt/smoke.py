import pathlib,json,urllib.request,subprocess,concurrent.futures,hashlib,shutil,time,threading,sys,os
R=pathlib.Path(__file__).resolve().parent
S=R/'server';S.mkdir(exist_ok=True)
def download(url,p):
 p.parent.mkdir(parents=True,exist_ok=True)
 for i in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Spore-Rebuilt-Test'}),timeout=120) as r:p.write_bytes(r.read())
   return
  except Exception:
   if i==3:raise
   time.sleep(3)
d=json.loads((R/'index.json').read_text());forge=d['dependencies']['forge']
installer=R/'installer.jar'
download(f'https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-{forge}/forge-1.20.1-{forge}-installer.jar',installer)
subprocess.run(['java','-jar',str(installer),'--installServer'],cwd=S,check=True)
def mod(f):
 if not f['path'].startswith('mods/') or f.get('env',{}).get('server')=='unsupported':return
 p=S/f['path'];download(f['downloads'][0],p)
 assert hashlib.sha512(p.read_bytes()).hexdigest()==f['hashes']['sha512'],f['path']
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:list(pool.map(mod,d['files']))
if (R/'overrides').exists():shutil.copytree(R/'overrides',S,dirs_exist_ok=True)
(S/'eula.txt').write_text('eula=true\n')
(S/'server.properties').write_text('online-mode=false\nserver-ip=127.0.0.1\nserver-port=25585\nview-distance=4\nsimulation-distance=4\nmax-players=1\ndifficulty=hard\nspawn-protection=0\n')
args=S/f'libraries/net/minecraftforge/forge/1.20.1-{forge}/unix_args.txt'
cmd=['java','-Xms1G','-Xmx5G','@'+str(args),'nogui']
p=subprocess.Popen(cmd,cwd=S,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
started=threading.Event();lines=[]
def watch():
 with (R/'server-smoke.log').open('w') as out:
  for line in p.stdout:
   out.write(line);out.flush();lines.append(line)
   print(line,end='',flush=True)
   if 'Done (' in line:started.set()
thread=threading.Thread(target=watch);thread.start()
deadline=time.time()+540
while not started.is_set() and p.poll() is None and time.time()<deadline:time.sleep(1)
if not started.is_set():
 p.terminate();thread.join(timeout=20);raise RuntimeError('Server did not reach Done')
for c in ['incontrol reload','incontrol showmobs','incontrol days 100','incontrol phases','save-all']:
 p.stdin.write(c+'\n');p.stdin.flush();time.sleep(3)
p.stdin.write('stop\n');p.stdin.flush();p.wait(timeout=120);thread.join()
text=''.join(lines)
assert p.returncode==0
assert 'Unknown command' not in text
(R/'smoke-result.json').write_text(json.dumps({'server_started':True,'clean_shutdown':True,'forge':forge,'mods':len(list((S/'mods').glob('*.jar')))},indent=2))
