package slimeknights.tconstruct.library.recipe.input;

import net.minecraft.world.item.ItemStack;
import slimeknights.mantle.recipe.input.SingleItemInput;

/** Single-slot recipe view retaining TConstruct's named stack accessor. */
@FunctionalInterface
public interface TinkerSingleItemInput extends SingleItemInput, TinkerRecipeInput {
  ItemStack getStack();

  @Override
  default ItemStack getItem() { return getStack(); }
}
