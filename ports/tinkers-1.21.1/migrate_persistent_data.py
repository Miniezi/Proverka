"""Move persistent modifier NBT storage to a serialized, copy-on-death attachment."""
import re

def migrate(root):
 java=root/'src/main/java'
 f=java/'slimeknights/tconstruct/library/tools/capability/PersistentDataCapability.java'
 s=f.read_text()
 # Preserve the existing explicit login/respawn/dimension sync handlers.
 sync=s[s.index('  /** Syncs the data to the given player */'):s.index('  /** Capability provider instance */')]
 start=sync.index('  /** copy caps when the player respawns/returns from the end */')
 end=sync.index('  /** sync caps when the player respawns/returns from the end */',start)
 sync=sync[:start]+sync[end:]
 sync=sync.replace('player.getCapability(CAPABILITY)', 'findData(player)')
 s="""package slimeknights.tconstruct.library.tools.capability;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import slimeknights.tconstruct.TConstruct;
import slimeknights.tconstruct.common.network.SyncPersistentDataPacket;
import slimeknights.tconstruct.common.network.TinkerNetwork;
import slimeknights.tconstruct.library.tools.nbt.ModDataNBT;
import java.util.Optional;

/** Persistent modifier data. NeoForge owns serialization and player clone copying. */
public final class PersistentDataCapability {
  private PersistentDataCapability() {}
  public static final DeferredHolder<AttachmentType<?>, AttachmentType<CompoundTag>> CAPABILITY = PersistentDataAttachment.TYPE;

  public static Optional<ModDataNBT> findData(Entity entity) {
    return entity instanceof LivingEntity || EntityModifierCapability.supportCapability(entity)
      ? Optional.of(ModDataNBT.readFromNBT(entity.getData(CAPABILITY))) : Optional.empty();
  }

  public static ModDataNBT getOrWarn(Entity entity) {
    return findData(entity).orElseGet(() -> {
      TConstruct.LOG.warn("Missing Tinkers NBT on entity {}, this should not happen", entity.getType());
      return new ModDataNBT();
    });
  }

  public static void register() {
    NeoForge.EVENT_BUS.addListener(PersistentDataCapability::playerRespawn);
    NeoForge.EVENT_BUS.addListener(PersistentDataCapability::playerChangeDimension);
    NeoForge.EVENT_BUS.addListener(PersistentDataCapability::playerLoggedIn);
  }

"""+sync+'}\n'
 f.write_text(s)
 count=1
 for f in java.rglob('*.java'):
  if f.name=='PersistentDataCapability.java':continue
  s=f.read_text();before=s
  s=re.sub(r'([\w]+(?:\.[\w]+|\(\))*)\.getCapability\(PersistentDataCapability\.CAPABILITY\)',r'PersistentDataCapability.findData(\1)',s)
  s=re.sub(r'(PersistentDataCapability\.findData\([^;]*?\))\.resolve\(\)',r'\1',s)
  if f.name=='TinkerModifiers.java':
   s=s.replace('  public TinkerModifiers() {','  public TinkerModifiers() {\n    slimeknights.tconstruct.library.tools.capability.PersistentDataAttachment.register(slimeknights.tconstruct.TConstruct.getModEventBus());')
  if s!=before:f.write_text(s);count+=1
 return count
