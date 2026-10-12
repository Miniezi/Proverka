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
import net.minecraft.world.entity.Entity;
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
  public static Optional<Holder> findData(Entity entity) { return entity instanceof LivingEntity living ? Optional.of(getData(living)) : Optional.empty(); }

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
 # The client equipment cache shares the already registered transient attachment.
 f=java/'slimeknights/tconstruct/tools/logic/EquipmentChangeWatcher.java'
 s=f.read_text()
 for line in s.splitlines(True):
  if any(x in line for x in ['import net.neoforged.neoforge.common.capabilities.', 'import net.neoforged.neoforge.common.util.LazyOptional;', 'import net.neoforged.neoforge.event.AttachCapabilitiesEvent;']):s=s.replace(line,'')
 s=s.replace('import net.minecraft.core.Direction;', 'import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability;')
 start=s.index('  /** Capability ID */');end=s.index('  /** Registers this capability */',start)
 s=s[:start]+"""  private static final TinkerDataCapability.TinkerDataKey<PlayerLastEquipment> LAST_EQUIPMENT =
    new TinkerDataCapability.TinkerDataKey<>(TConstruct.getResource("equipment_watcher"));

"""+s[end:]
 s=''.join(line for line in s.splitlines(True) if 'RegisterCapabilitiesEvent.class' not in line and 'addGenericListener(Entity.class' not in line)
 start=s.index('  /** Event listener to attach the capability */');end=s.index('  /** Client side modifier hooks */',start)
 s=s[:start]+s[end:]
 s=s.replace('      event.getEntity().getCapability(CAPABILITY).ifPresent(PlayerLastEquipment::update);',"""      Player player = event.getEntity();
      TinkerDataCapability.Holder data = TinkerDataCapability.getData(player);
      PlayerLastEquipment equipment = data.get(LAST_EQUIPMENT);
      if (equipment == null) {
        equipment = new PlayerLastEquipment(player);
        data.put(LAST_EQUIPMENT, equipment);
      }
      equipment.update();""")
 s=s.replace(' implements ICapabilityProvider, Runnable', '')
 s=s.replace('    private LazyOptional<PlayerLastEquipment> capability;\n','')
 s=s.replace('      this.capability = LazyOptional.of(() -> this);\n','')
 start=s.index('    /** Called on capability invalidate to invalidate */')
 s=s[:start]+'  }\n}\n'
 for imp in ['net.minecraft.resources.ResourceLocation','net.minecraft.world.entity.Entity','net.neoforged.bus.api.EventPriority','net.neoforged.fml.LogicalSide','javax.annotation.Nonnull']:
  s=s.replace('import '+imp+';\n','')
 s=s.replace('Capability to make it easy for modifiers to store common data on the player, primarily used for armor','Dispatches equipment changes; the client snapshot is transient per-player attachment data.')
 s=s.replace('/** Registers this capability */','/** Registers equipment listeners. Attachment registration is owned by TinkerDataCapability. */')
 s=s.replace('// only run for client side players every 5 ticks','// Preserve the original post-tick client update timing.')
 s=s.replace('      // run twice a second, should be plenty fast enough\n','')
 f.write_text(s)
 return count+1
