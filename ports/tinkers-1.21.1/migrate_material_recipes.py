"""Use 1.21 map/stream codecs for the three material-aware crafting recipes."""
from pathlib import Path
import json

def migrate(root):
    folder = root/'src/main/java/slimeknights/tconstruct/library/recipe/material'
    for name in ('ShapedMaterialsRecipe', 'ShapedMaterialRecipe', 'ShapelessMaterialsRecipe'):
        path = folder/(name+'.java')
        source = path.read_text()
        source = source.replace('import slimeknights.mantle.recipe.helper.LoggingRecipeSerializer;', '''import com.mojang.serialization.MapCodec;
import com.mojang.serialization.Codec;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.world.item.crafting.ShapedRecipePattern;
import slimeknights.mantle.data.loadable.LoadableCodec;
import slimeknights.mantle.data.loadable.StreamableCodec;''')
        if name=='ShapedMaterialsRecipe':
            begin=source.index('  public ShapedMaterialsRecipe(')
            end=source.index('\n  @Override',begin)
            source=source[:begin]+'''  private final MaterialRecipePattern materialPattern;
  public ShapedMaterialsRecipe(String group, CraftingBookCategory category, MaterialRecipePattern pattern, ItemStack result, boolean showNotification, List<MaterialVariantId> extraMaterials) {
    super(group, category, pattern.pattern(), result, showNotification);
    this.materialPattern = pattern;
    this.parts = pattern.parts();
    this.checkRepeats = parts.stream().distinct().count() == parts.size();
    this.extraMaterials = List.copyOf(extraMaterials);
  }
'''+source[end:]
            serializer='''  public static class Serializer implements RecipeSerializer<ShapedMaterialsRecipe> {
    static final Loadable<List<MaterialVariantId>> EXTRA_MATERIALS = MaterialVariantId.LOADABLE.list(0);
    static final LoadableField<List<MaterialVariantId>,ShapedMaterialsRecipe> MATERIAL_FIELD = EXTRA_MATERIALS.defaultField("extra_materials", List.of(), recipe -> recipe.extraMaterials);
    static final Codec<List<MaterialVariantId>> EXTRA_CODEC = new LoadableCodec<>(EXTRA_MATERIALS);
    static final StreamCodec<RegistryFriendlyByteBuf,List<MaterialVariantId>> EXTRA_STREAM = new StreamableCodec<>(EXTRA_MATERIALS);
    private static final MapCodec<ShapedMaterialsRecipe> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
      Codec.STRING.optionalFieldOf("group", "").forGetter(ShapedMaterialsRecipe::getGroup),
      CraftingBookCategory.CODEC.optionalFieldOf("category", CraftingBookCategory.MISC).forGetter(ShapedMaterialsRecipe::category),
      MaterialRecipePattern.CODEC.forGetter(recipe -> recipe.materialPattern),
      ItemStack.STRICT_CODEC.fieldOf("result").forGetter(recipe -> recipe.getResultItem(net.minecraft.core.RegistryAccess.EMPTY)),
      Codec.BOOL.optionalFieldOf("show_notification", true).forGetter(ShapedMaterialsRecipe::showNotification),
      EXTRA_CODEC.optionalFieldOf("extra_materials", List.of()).forGetter(recipe -> recipe.extraMaterials)
    ).apply(instance, ShapedMaterialsRecipe::new));
    private static final StreamCodec<RegistryFriendlyByteBuf,ShapedMaterialsRecipe> STREAM = StreamCodec.of((buffer, recipe) -> {
      buffer.writeUtf(recipe.getGroup());
      buffer.writeEnum(recipe.category());
      MaterialRecipePattern.STREAM_CODEC.encode(buffer, recipe.materialPattern);
      ItemStack.STREAM_CODEC.encode(buffer, recipe.getResultItem(net.minecraft.core.RegistryAccess.EMPTY));
      buffer.writeBoolean(recipe.showNotification());
      EXTRA_STREAM.encode(buffer, recipe.extraMaterials);
    }, buffer -> new ShapedMaterialsRecipe(buffer.readUtf(), buffer.readEnum(CraftingBookCategory.class),
      MaterialRecipePattern.STREAM_CODEC.decode(buffer), ItemStack.STREAM_CODEC.decode(buffer), buffer.readBoolean(), EXTRA_STREAM.decode(buffer)));
    @Override public MapCodec<ShapedMaterialsRecipe> codec() { return CODEC; }
    @Override public StreamCodec<RegistryFriendlyByteBuf,ShapedMaterialsRecipe> streamCodec() { return STREAM; }
  }
}'''
        elif name=='ShapelessMaterialsRecipe':
            source=source.replace('public ShapelessMaterialsRecipe(ResourceLocation id, String group,','public ShapelessMaterialsRecipe(String group,').replace('super(id, group, category, result, ingredients);','super(group, category, result, ingredients);')
            source=source.replace('this(recipe.getId(), recipe.getGroup(), recipe.category(), recipe.result, recipe.getIngredients(), partCount, extraMaterials);','this(recipe.getGroup(), recipe.category(), recipe.getResultItem(net.minecraft.core.RegistryAccess.EMPTY), recipe.getIngredients(), partCount, extraMaterials);')
            source=source.replace('    this.partCount = partCount;','    if (partCount < 1 || partCount > ingredients.size()) throw new IllegalArgumentException("Parts must be between 1 and the ingredient count");\n    this.partCount = partCount;')
            serializer='''  public static class Serializer implements RecipeSerializer<ShapelessMaterialsRecipe> {
    private static final MapCodec<ShapelessMaterialsRecipe> CODEC = RecordCodecBuilder.<RecipeData>mapCodec(instance -> instance.group(
      RecipeSerializer.SHAPELESS_RECIPE.codec().forGetter(RecipeData::recipe),
      Codec.INT.fieldOf("parts").forGetter(RecipeData::parts),
      ShapedMaterialsRecipe.Serializer.EXTRA_CODEC.optionalFieldOf("extra_materials", List.of()).forGetter(RecipeData::extra)
    ).apply(instance, RecipeData::new)).flatXmap(data -> {
      if (data.parts < 1 || data.parts > data.recipe.getIngredients().size()) return DataResult.error(() -> "Parts must be between 1 and the ingredient count");
      return DataResult.success(new ShapelessMaterialsRecipe(data.recipe, data.parts, data.extra));
    }, recipe -> DataResult.success(new RecipeData(recipe, recipe.partCount, recipe.extraMaterials)));
    private record RecipeData(ShapelessRecipe recipe, int parts, List<MaterialVariantId> extra) {}
    private static final StreamCodec<RegistryFriendlyByteBuf,ShapelessMaterialsRecipe> STREAM = StreamCodec.of((buffer, recipe) -> {
      RecipeSerializer.SHAPELESS_RECIPE.streamCodec().encode(buffer, recipe);
      buffer.writeVarInt(recipe.partCount);
      ShapedMaterialsRecipe.Serializer.EXTRA_STREAM.encode(buffer, recipe.extraMaterials);
    }, buffer -> new ShapelessMaterialsRecipe(RecipeSerializer.SHAPELESS_RECIPE.streamCodec().decode(buffer), buffer.readVarInt(), ShapedMaterialsRecipe.Serializer.EXTRA_STREAM.decode(buffer)));
    @Override public MapCodec<ShapelessMaterialsRecipe> codec() { return CODEC; }
    @Override public StreamCodec<RegistryFriendlyByteBuf,ShapelessMaterialsRecipe> streamCodec() { return STREAM; }
  }
}'''
        else:
            begin=source.index('  public ShapedMaterialRecipe(')
            end=source.index('  /** Gets the material to match */',begin)
            source=source[:begin]+'''  public ShapedMaterialRecipe(ShapedRecipe recipe, List<MaterialVariantId> extraMaterials) {
    super(recipe.getGroup(), recipe.category(), recipe.pattern, recipe.getResultItem(net.minecraft.core.RegistryAccess.EMPTY), recipe.showNotification());
    this.extraMaterials = List.copyOf(extraMaterials);
  }

'''+source[end:]
            source=source.replace('getId());','getGroup());')
            serializer='''  public static class Serializer implements RecipeSerializer<ShapedMaterialRecipe> {
    static final Loadable<List<MaterialVariantId>> EXTRA_MATERIALS = ShapedMaterialsRecipe.Serializer.EXTRA_MATERIALS;
    static final LoadableField<List<MaterialVariantId>,ShapedMaterialRecipe> MATERIAL_FIELD = EXTRA_MATERIALS.defaultField("extra_materials", List.of(), recipe -> recipe.extraMaterials);
    private record RecipeData(ShapedRecipe recipe, List<MaterialVariantId> extra) {}
    private static final MapCodec<ShapedMaterialRecipe> CODEC = RecordCodecBuilder.<RecipeData>mapCodec(instance -> instance.group(
      RecipeSerializer.SHAPED_RECIPE.codec().forGetter(RecipeData::recipe),
      ShapedMaterialsRecipe.Serializer.EXTRA_CODEC.optionalFieldOf("extra_materials", List.of()).forGetter(RecipeData::extra)
    ).apply(instance, RecipeData::new)).flatXmap(data -> {
      ShapedMaterialRecipe recipe = new ShapedMaterialRecipe(data.recipe, data.extra);
      if (recipe.getMaterial() == null) return DataResult.error(() -> "Invalid material ingredients for shaped material recipe");
      return DataResult.success(recipe);
    }, recipe -> DataResult.success(new RecipeData(recipe, recipe.extraMaterials)));
    private static final StreamCodec<RegistryFriendlyByteBuf,ShapedMaterialRecipe> STREAM = StreamCodec.of((buffer, recipe) -> {
      RecipeSerializer.SHAPED_RECIPE.streamCodec().encode(buffer, recipe);
      ShapedMaterialsRecipe.Serializer.EXTRA_STREAM.encode(buffer, recipe.extraMaterials);
    }, buffer -> new ShapedMaterialRecipe(RecipeSerializer.SHAPED_RECIPE.streamCodec().decode(buffer), ShapedMaterialsRecipe.Serializer.EXTRA_STREAM.decode(buffer)));
    @Override public MapCodec<ShapedMaterialRecipe> codec() { return CODEC; }
    @Override public StreamCodec<RegistryFriendlyByteBuf,ShapedMaterialRecipe> streamCodec() { return STREAM; }
  }
}'''
        source=source[:source.index('  public static class Serializer')]+serializer+'\n'
        path.write_text(source)
    migrated_resources = 0
    recipe_types = {'tconstruct:crafting_shaped_material', 'tconstruct:crafting_shaped_materials', 'tconstruct:crafting_shapeless_materials'}
    for resources in (root/'src/main/resources', root/'src/generated/resources'):
        for path in list((resources/'data').glob('*/recipes/**/*.json')):
            data = json.loads(path.read_text())
            if data.get('type') not in recipe_types:
                continue
            result = data['result']
            if 'item' in result:
                result['id'] = result.pop('item')
            if 'nbt' in result:
                nbt = result.pop('nbt')
                if not isinstance(nbt, dict) or set(nbt) != {'display'} or set(nbt['display']) != {'Name'}:
                    raise ValueError(f'Unsupported legacy recipe result NBT: {path}')
                result.setdefault('components', {})['minecraft:custom_name'] = nbt['display']['Name']
            relative = path.relative_to(resources/'data')
            target = resources/'data'/relative.parts[0]/'recipe'/Path(*relative.parts[2:])
            if target.exists():
                raise ValueError(f'Recipe migration target already exists: {target}')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, indent=2)+'\n')
            path.unlink()
            migrated_resources += 1
    return {'serializers': 3, 'recipe_resources': migrated_resources}
