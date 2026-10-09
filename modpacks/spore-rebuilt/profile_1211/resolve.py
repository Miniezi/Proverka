"""Resolve a clean NeoForge 1.21.1 candidate using publisher metadata."""
import json, urllib.request, urllib.parse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).parent
HEADERS={'User-Agent':'SporeRebuilt/0.1 (compatibility audit)'}
def get(path):
    with urllib.request.urlopen(urllib.request.Request('https://api.modrinth.com/v2/'+path,headers=HEADERS),timeout=45) as r:return json.load(r)
def resolve(slug):
    q=urllib.parse.urlencode({'loaders':json.dumps(['neoforge']),'game_versions':json.dumps(['1.21.1'])})
    try:
        versions=get('project/'+slug+'/version?'+q)
        releases=[v for v in versions if v['version_type']=='release']
        v=next(iter(releases or versions),None)
        if not v:return {'requested':slug,'error':'No compatible version'}
        return {'requested':slug,'version':v}
    except Exception as e:return {'requested':slug,'error':str(e)}
def main():
    slugs=['mekanism','immersiveengineering','apotheosis','puffish-skills','minecraft-comes-alive-reborn','easy-villagers','jei','fungal-infection-spore','tacz']
    with ThreadPoolExecutor(max_workers=5) as pool: roots=list(pool.map(resolve,slugs))
    versions={r['version']['id']:r['version'] for r in roots if 'version' in r}
    errors=[r for r in roots if 'error' in r]
    todo=list(versions.values());seen=set()
    while todo:
        v=todo.pop()
        for d in v['dependencies']:
            if d['dependency_type']!='required':continue
            key=d.get('version_id') or d.get('project_id')
            if not key or key in seen:continue
            seen.add(key)
            try:
                if d.get('version_id'):child=get('version/'+d['version_id'])
                else:
                    r=resolve(d['project_id'])
                    if 'error' in r:raise ValueError(r['error'])
                    child=r['version']
                if '1.21.1' not in child['game_versions'] or 'neoforge' not in child['loaders']:raise ValueError('Dependency incompatible with target')
                if child['id'] not in versions:versions[child['id']]=child;todo.append(child)
            except Exception as e:errors.append({'parent':v['name'],'dependency':d,'error':str(e)})
    result={'target':{'minecraft':'1.21.1','loader':'neoforge'},'launch_tested':False,'roots':roots,'versions':list(versions.values()),'unresolved':errors}
    (ROOT/'modrinth-candidate.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for r in roots:print(r['requested'],r.get('error') or r['version']['version_number'])
    print('Resolved versions:',len(versions),'Unresolved:',len(errors))
if __name__=='__main__':main()
