package slimeknights.tconstruct.library.recipe.input;

import net.minecraft.world.item.crafting.RecipeInput;

/** Recipe view only: inventory ownership and mutations remain with the machine. */
public interface TinkerRecipeInput extends RecipeInput {
  /** Legacy read-only size accessor for machine recipe callers. */
  @Deprecated
  default int getContainerSize() { return size(); }
}
