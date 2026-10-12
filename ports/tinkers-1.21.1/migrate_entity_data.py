"""Replace the nonpersistent living-entity data capability with a lazy attachment."""
import re

def migrate(root):
 java=root/'src/main/java'
 f=java/'slimeknights/tconstruct/library/tools/capability/TinkerDataCapability.java'
 s=f.read_text();body=s[s.index('  /** Class for generic keys */'):]
 body=body.replace('    @Override\n    public String toString()', '    @Override\n    public ResourceLocation id() { return id; }\n\n    @Override\n    public String toString()')
 header='''package slimeknights.tconstruct.library.tools.capability;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import slimeknights.mantle.registration.object.IdAwareObject;
import javax.annotation.Nullable;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.function.Supplier;

/** Transient equipment-derived data. Intentionally not serialized, synced, or copied on death. */
public class TinkerDataCapability {
  private TinkerDataCapability() {}
  private static final DeferredRegister<AttachmentType<?>> ATTACHMENTS = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, "tconstruct");
  /** Legacy field name retained for the new attachment registry holder. */
  public static final DeferredHolder<AttachmentType<?>, AttachmentType<Holder>> CAPABILITY = ATTACHMENTS.register("modifier_data", () -> AttachmentType.builder(Holder::new).build());

  /** Must run during mod construction, before attachment registration closes. */
  public static void register(IEventBus bus) { ATTACHMENTS.register(bus); }

  public static Holder getData(LivingEntity entity) { return entity.getData(CAPABILITY); }
  public static Optional<Holder> findData(LivingEntity entity) { return Optional.of(getData(entity)); }

'''
 f.write_text(header+body)
 count=0
 for f in java.rglob('*.java'):
  if f.name=='TinkerDataCapability.java':continue
  s=f.read_text();before=s
  s=re.sub(r'([\w]+(?:\.[\w]+|\(\))*)\.getCapability\(TinkerDataCapability\.CAPABILITY\)',r'TinkerDataCapability.findData(\1)',s)
  s=re.sub(r'(TinkerDataCapability\.findData\([^;]*?\))\.resolve\(\)',r'\1',s)
  names=re.findall(r'LazyOptional<TinkerDataCapability\.Holder>\s+(\w+)',s)
  s=s.replace('LazyOptional<TinkerDataCapability.Holder>', 'java.util.Optional<TinkerDataCapability.Holder>')
  for name in names:
   s=s.replace(name+'.resolve()',name)
   s=s.replace('LogicHelper.orElseNull('+name+')',name+'.orElse(null)')
  s=s.replace('LogicHelper.orElseNull(context.getTinkerData())', 'context.getTinkerData().orElse(null)')
  s=s.replace('LogicHelper.orElseNull(getTinkerData())', 'getTinkerData().orElse(null)')
  if f.name=='TinkerModifiers.java':
   s=s.replace('    TinkerDataCapability.register();\n','')
   s=s.replace('  public TinkerModifiers() {', '  public TinkerModifiers() {\n    TinkerDataCapability.register(slimeknights.tconstruct.TConstruct.getModEventBus());')
  without_import=s.replace('import net.neoforged.neoforge.common.util.LazyOptional;\n','')
  if not re.search(r'\bLazyOptional\b',without_import):s=without_import
  if s!=before:f.write_text(s);count+=1
 return count
