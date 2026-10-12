package slimeknights.tconstruct.library.tools.capability;

import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.attachment.IAttachmentHolder;
import net.neoforged.neoforge.attachment.IAttachmentSerializer;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/** Mutable persistent modifier NBT. Network synchronization remains explicit. */
public final class PersistentDataAttachment {
  private PersistentDataAttachment() {}
  private static final DeferredRegister<AttachmentType<?>> TYPES = DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, "tconstruct");
  public static final DeferredHolder<AttachmentType<?>, AttachmentType<CompoundTag>> TYPE = TYPES.register("persistent_data", () ->
    AttachmentType.builder(CompoundTag::new).serialize(new IAttachmentSerializer<CompoundTag, CompoundTag>() {
      @Override
      public CompoundTag read(IAttachmentHolder holder, CompoundTag tag, HolderLookup.Provider registries) {
        return tag.copy();
      }
      @Override
      public CompoundTag write(CompoundTag data, HolderLookup.Provider registries) {
        return data.isEmpty() ? null : data.copy();
      }
    }).copyOnDeath().build());

  public static void register(IEventBus bus) { TYPES.register(bus); }
}
