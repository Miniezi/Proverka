package slimeknights.tconstruct.library.recipe.ingredient;

import com.google.gson.JsonObject;
import com.mojang.serialization.MapCodec;
import net.minecraft.network.RegistryFriendlyByteBuf;
import slimeknights.mantle.data.loadable.LoadableCodec;
import slimeknights.mantle.data.loadable.record.RecordLoadable;
import slimeknights.mantle.data.predicate.IJsonPredicate;
import slimeknights.mantle.util.typed.TypedMap;
import slimeknights.tconstruct.library.json.TinkerLoadables;
import slimeknights.tconstruct.library.json.predicate.material.MaterialPredicate;
import slimeknights.tconstruct.library.json.predicate.material.MaterialPredicateField;
import slimeknights.tconstruct.library.materials.definition.MaterialVariantId;

/** Retains compact material IDs, structured predicates and the legacy material_tag field. */
public record MaterialIngredientFilter(IJsonPredicate<MaterialVariantId> predicate) {
  private static final MaterialPredicateField<MaterialIngredientFilter> FIELD = new MaterialPredicateField<>("material", MaterialIngredientFilter::predicate);
  private static final RecordLoadable<MaterialIngredientFilter> LOADABLE = new RecordLoadable<>() {
    @Override public MaterialIngredientFilter deserialize(JsonObject json, TypedMap context) {
      var predicate = FIELD.get(json,context);
      if (json.has("material_tag")) {
        var tag = MaterialPredicate.tag(TinkerLoadables.MATERIAL_TAGS.getIfPresent(json,"material_tag",context));
        predicate = predicate == MaterialPredicate.ANY ? tag : MaterialPredicate.and(predicate,tag);
      }
      return new MaterialIngredientFilter(predicate);
    }
    @Override public void serializeInto(MaterialIngredientFilter value, JsonObject json, TypedMap context) { FIELD.serializeInto(value,json,context); }
    @Override public MaterialIngredientFilter decode(RegistryFriendlyByteBuf buffer, TypedMap context) { return new MaterialIngredientFilter(FIELD.decode(buffer,context)); }
    @Override public void encode(RegistryFriendlyByteBuf buffer, MaterialIngredientFilter value, TypedMap context) { FIELD.encode(buffer,value,context); }
  };
  public static final MapCodec<MaterialIngredientFilter> CODEC = MapCodec.assumeMapUnsafe(new LoadableCodec<>(LOADABLE));
}
