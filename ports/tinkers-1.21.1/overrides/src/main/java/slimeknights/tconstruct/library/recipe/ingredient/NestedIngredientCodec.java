package slimeknights.tconstruct.library.recipe.ingredient;

import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.crafting.Ingredient;

/** Accepts legacy inline item/tag fields; writes an explicit match to avoid recursive type dispatch. */
public final class NestedIngredientCodec {
  private NestedIngredientCodec() {}
  private static final MapCodec<Ingredient> INLINE = Codec.mapEither(
    BuiltInRegistries.ITEM.byNameCodec().validate(item -> item == net.minecraft.world.item.Items.AIR
      ? com.mojang.serialization.DataResult.error(() -> "Ingredient item cannot be air")
      : com.mojang.serialization.DataResult.success(item)).fieldOf("item"), TagKey.codec(Registries.ITEM).fieldOf("tag")
  ).xmap(value -> value.map(Ingredient::of, Ingredient::of), value -> {
    throw new UnsupportedOperationException("Nested ingredients are encoded with match");
  });
  public static final MapCodec<Ingredient> CODEC = Codec.mapEither(
    Ingredient.CODEC_NONEMPTY.fieldOf("match"), INLINE
  ).xmap(value -> value.map(ingredient -> ingredient, ingredient -> ingredient), Either::left);
}
