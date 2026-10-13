package slimeknights.tconstruct.library.recipe.material;

import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.ShapedRecipePattern;

/** Recipe pattern and material-part order, decoded together to preserve ingredient identity. */
public final class MaterialRecipePattern {
  private record Definition(ShapedRecipePattern.Data pattern, String parts) {
    private static final MapCodec<Definition> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
      ShapedRecipePattern.Data.MAP_CODEC.forGetter(Definition::pattern),
      Codec.STRING.fieldOf("parts").forGetter(Definition::parts)
    ).apply(instance, Definition::new));
  }

  public static final MapCodec<MaterialRecipePattern> CODEC = Definition.CODEC.flatXmap(definition -> {
    try {
      return DataResult.success(new MaterialRecipePattern(definition));
    } catch (IllegalArgumentException exception) {
      return DataResult.error(exception::getMessage);
    }
  }, value -> DataResult.success(value.definition));

  // Registry-aware encoding preserves custom ingredients and their components.
  // Retaining key/pattern metadata also permits JSON serialization after a wire roundtrip.
  public static final StreamCodec<RegistryFriendlyByteBuf, MaterialRecipePattern> STREAM_CODEC =
    ByteBufCodecs.fromCodecWithRegistries(CODEC.codec());

  private final Definition definition;
  private final ShapedRecipePattern pattern;
  private final List<Ingredient> parts;

  private MaterialRecipePattern(Definition definition) {
    this.definition = definition;
    this.pattern = ShapedRecipePattern.of(definition.pattern.key(), definition.pattern.pattern());
    List<Ingredient> parts = new ArrayList<>(definition.parts.length());
    for (int index = 0; index < definition.parts.length(); index++) {
      char symbol = definition.parts.charAt(index);
      Ingredient ingredient = definition.pattern.key().get(symbol);
      if (ingredient == null) {
        throw new IllegalArgumentException("Parts references symbol '" + symbol + "' but it is not defined in the key");
      }
      parts.add(ingredient);
    }
    this.parts = List.copyOf(parts);
  }

  public ShapedRecipePattern pattern() { return pattern; }
  public List<Ingredient> parts() { return parts; }
}
