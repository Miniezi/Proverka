"""First mechanical API migration. This does not constitute a working port."""
from pathlib import Path
import re,difflib,json
P=Path(__file__).resolve().parent;root=P/'TinkersConstruct-1.20.1';changes=[];count=0
# Tokenize comments and literals as indivisible tokens so commas inside calls/strings are ignored.
pattern=re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\w+|[^\s]',re.M)
for f in root.rglob('*.java'):
 before=f.read_text();tokens=list(pattern.finditer(before));edits=[]
 for i in range(len(tokens)-3):
  if [t.group() for t in tokens[i:i+3]]!=['new','ResourceLocation','(']:continue
  depth=1;commas=0
  for t in tokens[i+3:]:
   v=t.group()
   if v in ['(','[','{']:depth+=1
   elif v in [')',']','}']:
    depth-=1
    if depth==0:break
   elif v==',' and depth==1:commas+=1
  assert depth==0 and commas in [0,1],(f,tokens[i].start())
  replacement='ResourceLocation.'+('parse' if commas==0 else 'fromNamespaceAndPath')+'('
  edits.append((tokens[i].start(),tokens[i+2].end(),replacement));count+=1
 after=before
 for a,b,v in reversed(edits):after=after[:a]+v+after[b:]
 if after!=before:
  name=f.relative_to(root).as_posix();changes.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+name,tofile='b/'+name));f.write_text(after)
if changes:(P/'resource-location.patch').write_text(''.join(changes))
print('Migrated constructor calls:',count,'patch bytes:',(P/'resource-location.patch').stat().st_size)
