"""Migrate custom Mantle loadables to registry buffers and contextual serialization."""
import re

def migrate(root):
 count=0;methods=0
 for f in (root/'src/main/java').rglob('*.java'):
  s=f.read_text()
  if 'import slimeknights.mantle.data.loadable.' not in s:continue
  if not re.search(r'(?:implements|extends|new)\s+[^;{\n]*(?:Loadable|Streamable)[<\s]',s):continue
  before=s
  s=re.sub(r'\bFriendlyByteBuf\b','RegistryFriendlyByteBuf',s)
  pattern=r'(@Override\s+public\s+(?:[\w<>?,.]+\s+)+)(encode|decode|getString|serialize)\(([^)]*)\)'
  def update(m):
   nonlocal methods
   prefix,name,args=m.groups()
   if name=='decode':return m.group(0)
   if 'TypedMap' in args:return m.group(0)
   if name=='encode' and not args.startswith('RegistryFriendlyByteBuf '):return m.group(0)
   if name=='serialize' and 'JsonObject ' in args:name='serializeInto'
   methods+=1
   return prefix+name+'('+args+', slimeknights.mantle.util.typed.TypedMap context)'
  s=re.sub(pattern,update,s)
  if f.name=='OptionallyNestedLoadable.java':
   s=s.replace('loadable.serialize(object)', 'loadable.serialize(object, context)')
   s=s.replace('loadable.encode(buffer, value)', 'loadable.encode(buffer, value, context)')
  s=s.replace('buffer.readAnySizeNbt()', 'buffer.readNbt()')
  if s!=before:f.write_text(s);count+=1
 return {'files':count,'methods':methods}
