package slimeknights.tconstruct.library.recipe.ingredient;

import com.mojang.serialization.MapCodec;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ItemLike;
import net.neoforged.neoforge.common.crafting.IngredientType;

/** Matches the nested ingredient only if crafting will not return a container. */
public final class NoContainerIngredient extends NestedIngredient {
  public static final ResourceLocation ID = ResourceLocation.fromNamespaceAndPath("tconstruct", "no_container");
  public static final MapCodec<NoContainerIngredient> CODEC = NestedIngredientCodec.CODEC.xmap(NoContainerIngredient::new, value -> value.nested);
  public static final IngredientType<NoContainerIngredient> TYPE = new IngredientType<>(CODEC);
  public NoContainerIngredient(Ingredient nested) { super(nested); }
  @Override public boolean test(ItemStack stack) { return super.test(stack) && !stack.hasCraftingRemainingItem(); }
  @Override public boolean isSimple() { return false; }
  @Override public IngredientType<?> getType() { return TYPE; }
  public static Ingredient of(Ingredient ingredient) { return new NoContainerIngredient(ingredient).toVanilla(); }
  public static Ingredient of(ItemLike... items) { return of(Ingredient.of(items)); }
  public static Ingredient of(ItemStack... stacks) { return of(Ingredient.of(stacks)); }
  public static Ingredient of(TagKey<Item> tag) { return of(Ingredient.of(tag)); }
}
