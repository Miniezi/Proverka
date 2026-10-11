from pathlib import Path
import urllib.request,hashlib,json,concurrent.futures
P=Path(__file__).resolve().parent;out=P/'compat-libs';out.mkdir(exist_ok=True)
def get(pair):
 name,data=pair;p=out/(name+'.jar')
 if p.exists() and hashlib.sha512(p.read_bytes()).hexdigest()==data['sha512']:return
 b=urllib.request.urlopen(data['url'],timeout=120).read();assert hashlib.sha512(b).hexdigest()==data['sha512'],name;p.write_bytes(b);print('Verified',name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(get,json.loads((P/'compat-dependencies.json').read_text()).items()))
