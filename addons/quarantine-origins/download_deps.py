from pathlib import Path
import urllib.request,json,hashlib
P=Path(__file__).resolve().parent
for name,f in json.loads((P/'dependencies.json').read_text()).items():
 b=urllib.request.urlopen(f['url'],timeout=120).read();assert hashlib.sha512(b).hexdigest()==f['sha512'],name
 p=P/'libs'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(b)
 print('Verified',name)
