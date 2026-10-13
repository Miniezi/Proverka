"""Remove the old unchecked Dummy constructor path from all typed identifiers."""
import re

def migrate(root):
 java=root/'src/main/java'
 count=0
 for f in java.rglob('*.java'):
  s=f.read_text()
  if 'extends ResourceId' not in s:continue
  name=f.stem
  s=re.sub(r'  private '+name+r'\(String namespace, String path, @Nullable Dummy pDummy\) \{\s+super\(namespace, path, pDummy\);\s+\}\n','',s)
  s=re.sub(r'new '+name+r'\((\w+), (\w+), null\)',r'new '+name+r'(\1, \2)',s)
  assert 'Dummy' not in s,f
  f.write_text(s);count+=1
 # Keep the upstream SRG transformer list as migration reference only.
 at=root/'src/main/resources/META-INF/accesstransformer.cfg'
 if at.exists():at.rename(at.with_name('accesstransformer-1.20.1-reference.txt'))
 f=java/'slimeknights/tconstruct/TConstruct.java';s=f.read_text()
 s=s.replace('import net.neoforged.neoforge.registries.MissingMappingsEvent;\n','')
 s=s.replace('NeoForge.EVENT_BUS.addListener(TConstruct::missingMappings);','getModEventBus().addListener(slimeknights.tconstruct.common.registration.TinkerRegistryAliases::register);')
 start=s.index('  /** Handles missing mappings of all types */');end=s.index('  /* Utils */',start)
 s=s[:start]+s[end:];f.write_text(s)
 return count
