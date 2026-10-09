import json,hashlib,urllib.request,zipfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
P=Path(__file__).parent
D=P/'mods';D.mkdir(exist_ok=True)
def download(v):
 f=next((f for f in v['files'] if f['primary']),v['files'][0]);p=D/f['filename']
 for attempt in range(3):
  try:
   if not p.exists():
    with urllib.request.urlopen(f['url'],timeout=90) as r:p.write_bytes(r.read())
   b=p.read_bytes()
   assert len(b)==f['size']
   for alg,h in f['hashes'].items():assert hashlib.new(alg,b).hexdigest()==h
   with zipfile.ZipFile(p) as z:assert z.testzip() is None
   return p.name
  except Exception:
   p.unlink(missing_ok=True)
   if attempt==2:raise
if __name__=='__main__':
 d=json.loads((P/'modrinth-candidate.json').read_text())
 with ThreadPoolExecutor(max_workers=8) as ex:
  for f in ex.map(download,d['versions']):print(f,flush=True)
