package slimeknights.tconstruct.smeltery.capability;

import java.util.function.Supplier;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.items.IItemHandler;
import slimeknights.mantle.inventory.EmptyItemHandler;

/** Stable item view that stops accessing an unformed or replaced controller. */
public final class ResolvingItemHandler implements IItemHandler {
  private final Supplier<IItemHandler> resolve;
  public ResolvingItemHandler(Supplier<IItemHandler> resolve) { this.resolve = resolve; }
  private IItemHandler handler() {
    IItemHandler current = resolve.get();
    return current == null || current == this ? EmptyItemHandler.INSTANCE : current;
  }
  @Override public int getSlots() { return handler().getSlots(); }
  @Override public ItemStack getStackInSlot(int slot) { return handler().getStackInSlot(slot); }
  @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) { return handler().insertItem(slot, stack, simulate); }
  @Override public ItemStack extractItem(int slot, int amount, boolean simulate) { return handler().extractItem(slot, amount, simulate); }
  @Override public int getSlotLimit(int slot) { return handler().getSlotLimit(slot); }
  @Override public boolean isItemValid(int slot, ItemStack stack) { return handler().isItemValid(slot, stack); }
}
