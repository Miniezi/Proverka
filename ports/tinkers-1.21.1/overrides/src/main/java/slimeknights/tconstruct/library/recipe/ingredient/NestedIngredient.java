package slimeknights.tconstruct.library.recipe.ingredient;

import java.util.Arrays;
import java.util.Objects;
import java.util.stream.Stream;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.common.crafting.ICustomIngredient;

/** NeoForge owns the vanilla wrapper and its display cache. */
public abstract class NestedIngredient implements ICustomIngredient {
  protected final Ingredient nested;
  protected NestedIngredient(Ingredient nested) { this.nested = Objects.requireNonNull(nested); }
  @Override public boolean test(ItemStack stack) { return stack != null && nested.test(stack); }
  @Override public Stream<ItemStack> getItems() { return Arrays.stream(nested.getItems()); }
  @Override public boolean isSimple() { return nested.isSimple(); }
  @Override public boolean equals(Object other) {
    return other != null && getClass() == other.getClass() && nested.equals(((NestedIngredient)other).nested);
  }
  @Override public int hashCode() { return Objects.hash(getClass(), nested); }
}
