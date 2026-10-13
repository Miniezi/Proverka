package slimeknights.tconstruct.library.recipe.ingredient;

import com.mojang.datafixers.util.Either;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;

/** Inclusive material quantities. An omitted maximum means unbounded. */
public record MaterialValueRange(float min, float max) {
  private record Bounds(float min, float max) {}
  private static final Codec<Bounds> BOUNDS = RecordCodecBuilder.create(instance -> instance.group(
    Codec.FLOAT.optionalFieldOf("min",0f).forGetter(Bounds::min),
    Codec.FLOAT.optionalFieldOf("max",Float.POSITIVE_INFINITY).forGetter(Bounds::max)
  ).apply(instance, Bounds::new));
  public static final Codec<MaterialValueRange> CODEC = Codec.either(Codec.FLOAT,BOUNDS).comapFlatMap(value -> {
    Bounds bounds = value.map(number -> new Bounds(number,number), range -> range);
    try { return DataResult.success(new MaterialValueRange(bounds.min,bounds.max)); }
    catch (IllegalArgumentException exception) { return DataResult.error(exception::getMessage); }
  }, range -> range.min == range.max ? Either.left(range.min) : Either.right(new Bounds(range.min,range.max)));
  public MaterialValueRange {
    if (!Float.isFinite(min) || min < 0 || Float.isNaN(max) || max < min) {
      throw new IllegalArgumentException("Material quantity range must be nonnegative and ordered, with a finite minimum");
    }
  }
  public boolean test(float quantity) { return Float.isFinite(quantity) && min <= quantity && quantity <= max; }
}
