"""Migrate custom Mantle loadables to registry buffers and contextual serialization."""
import re

def migrate(root):
 count=0;methods=0
 for f in (root/'src/main/java').rglob('*.java'):
  s=f.read_text()
  if 'import slimeknights.mantle.data.loadable.' not in s:continue
  if not re.search(r'(?:implements|extends|new)\s+[^;{\n]*(?:Loadable|LoadableField|RecordField|Streamable)[<\s]',s):continue
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
  if f.name in ['MergingField.java','MergingListField.java']:
   for m in list(re.finditer(r'\bfield\.(serialize|encode)\(',s))[::-1]:
    start=m.end();end=start;depth=1
    while depth:
     depth+=(s[end]=='(')-(s[end]==')');end+=1
    args=s[start:end-1]
    method='serializeInto' if m[1]=='serialize' else 'encode'
    s=s[:m.start()]+'field.'+method+'('+args+', context)'+s[end:]
  if f.name=='StatLoadable.java':
   s=s.replace('buffer.writeId(BuiltInRegistries.STAT_TYPE, type);','buffer.writeVarInt(BuiltInRegistries.STAT_TYPE.getId(type));')
   s=s.replace('buffer.writeId(type.getRegistry(), value.getValue());','buffer.writeVarInt(type.getRegistry().getId(value.getValue()));')
   s=s.replace('registry == BuiltInRegistries.ENCHANTMENT', 'registry.key().equals(net.minecraft.core.registries.Registries.ENCHANTMENT)')
   s=s.replace('Component.translatable(((Enchantment) value).getDescriptionId())', '((Enchantment) value).description()')
  s=s.replace('buffer.readAnySizeNbt()', 'buffer.readNbt()')
  if s!=before:f.write_text(s);count+=1
 # RecordLoadable now distinguishes JSON-object emission from value serialization.
 call_files={'SimpleLevelingFormula.java','LevelingValue.java','RandomLevelingValue.java','AbstractMaterialRenderInfoProvider.java','AbstractFluidEffectProvider.java','MaterialPredicateField.java','LoadableFinishedRecipe.java'}
 for f in (root/'src/main/java').rglob('*.java'):
  if f.name not in call_files:continue
  s=f.read_text();before=s
  for m in list(re.finditer(r'\.serialize\(',s))[::-1]:
   start=m.end();end=start;depth=1
   while depth:
    depth+=(s[end]=='(')-(s[end]==')');end+=1
   args=s[start:end-1]
   if re.search(r',\s*(?:json|serialized)\s*$',args):s=s[:m.start()]+'.serializeInto('+args+')'+s[end:]
  if s!=before:f.write_text(s);count+=1
 return {'files':count,'methods':methods}
