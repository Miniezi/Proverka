package slimeknights.tconstruct.library.tools.nbt;

import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.world.item.ItemStack;

/** Registry-aware storage for item stacks nested in tool modifier data. */
public final class StoredItemStack {
  private StoredItemStack() {}

  /** Encode completely before the caller replaces its stored data. */
  public static CompoundTag write(ItemStack stack, HolderLookup.Provider registries) {
    if (stack.isEmpty()) return new CompoundTag();
    return (CompoundTag)ItemStack.CODEC.encodeStart(registries.createSerializationContext(NbtOps.INSTANCE),stack).getOrThrow();
  }

  /** Invalid or absent stored items follow vanilla's empty-stack fallback. */
  public static ItemStack read(CompoundTag data, HolderLookup.Provider registries) {
    return ItemStack.parseOptional(registries, data);
  }
}
