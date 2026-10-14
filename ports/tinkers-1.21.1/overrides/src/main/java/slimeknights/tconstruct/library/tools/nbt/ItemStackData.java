package slimeknights.tconstruct.library.tools.nbt;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import java.util.function.Consumer;

/** Copy-on-write access to mod-owned item data. Never exposes a component's mutable NBT. */
public final class ItemStackData {
  private ItemStackData() {}

  /** Returns a detached snapshot. Reading an empty stack does not create a component. */
  public static CompoundTag read(ItemStack stack) {
    return stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
  }

  /** Commits only after the edit succeeds, preserving unrelated custom keys and components. */
  public static void update(ItemStack stack, Consumer<CompoundTag> edit) {
    if (stack.isEmpty()) return;
    CompoundTag data = read(stack);
    edit.accept(data);
    if (data.isEmpty()) stack.remove(DataComponents.CUSTOM_DATA);
    else stack.set(DataComponents.CUSTOM_DATA, CustomData.of(data));
  }
}
