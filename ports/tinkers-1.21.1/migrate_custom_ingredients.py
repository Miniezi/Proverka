"""Migrate material and no-container ingredients to registered NeoForge ingredient types."""
import re

def migrate(root):
    folder=root/'src/main/java/slimeknights/tconstruct/library/recipe/ingredient'
    common='''import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.neoforged.neoforge.common.crafting.IngredientType;
import net.neoforged.neoforge.common.crafting.ICustomIngredient;
'''
    for name in ('MaterialIngredient','MaterialValueIngredient'):
        path=folder/(name+'.java');s=path.read_text()
        s=s.replace('import net.neoforged.neoforge.common.crafting.AbstractIngredient;','').replace('import net.neoforged.neoforge.common.crafting.IIngredientSerializer;','').replace('import net.neoforged.neoforge.common.crafting.VanillaIngredientSerializer;','')
        s=s.replace('import com.google.gson.JsonElement;',common+'import com.google.gson.JsonElement;')
        s=s.replace('extends AbstractIngredient','implements ICustomIngredient')
        s=s.replace('public static '+name+' of(', 'public static Ingredient of(')
        # Factory consumers expect vanilla Ingredients. Keep internal constructors/merge methods typed.
        s=re.sub(r'return new '+name+r'\(([^;\n]+)\);', lambda m:'return new '+name+'('+m[1]+').toVanilla();' if name=='MaterialIngredient' else m[0],s)
        if name=='MaterialIngredient':
            start=s.index('  @Override\n  public ItemStack[] getItems()')
            s=s[:start]+'''  @Override
  public Stream<ItemStack> getItems() {
    if (!MaterialRegistry.isFullyLoaded()) return Arrays.stream(nested.getItems());
    return Arrays.stream(nested.getItems())
      .filter(stack -> stack.getItem() instanceof IMaterialItem)
      .flatMap(stack -> MaterialRecipeCache.getAllVariants().stream().filter(material::matches)
        .map(variant -> IMaterialItem.withMaterial(stack,variant))).distinct();
  }
  @Override public boolean isSimple() { return material == MaterialPredicate.ANY && nested.isSimple(); }
  @Override public IngredientType<?> getType() { return TYPE; }
  @Override public boolean equals(Object other) {
    return super.equals(other) && material.equals(((MaterialIngredient)other).material);
  }
  @Override public int hashCode() { return java.util.Objects.hash(super.hashCode(),material); }
  public static final ResourceLocation ID = ResourceLocation.fromNamespaceAndPath("tconstruct","material");
  public static final MapCodec<MaterialIngredient> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
    NestedIngredientCodec.CODEC.forGetter(value -> value.nested),
    MaterialIngredientFilter.CODEC.forGetter(value -> new MaterialIngredientFilter(value.material))
  ).apply(instance, (nested,filter) -> new MaterialIngredient(nested,filter.predicate())));
  public static final IngredientType<MaterialIngredient> TYPE = new IngredientType<>(CODEC);
}
'''
            s=s.replace('  @Nullable\n  private ItemStack[] materialStacks;\n','')
        else:
            s=s.replace('return new MaterialValueIngredient(materials, minValue, maxValue);','return new MaterialValueIngredient(materials, minValue, maxValue).toVanilla();')
            start=s.index('  @Override\n  public ItemStack[] getItems()');end=s.index('  /* Helpers for ShapedMaterialRecipe */',start)
            s=s[:start]+'''  @Override
  public java.util.stream.Stream<ItemStack> getItems() {
    return MaterialRecipeCache.getSortedRecipes().stream().filter(this::test)
      .flatMap(recipe -> Arrays.stream(recipe.getIngredient().getItems()));
  }
  // Material recipe predicates must be checked live rather than reduced to item IDs.
  @Override public boolean isSimple() { return false; }

'''+s[end:]
            start=s.index('  /* JSON */')
            s=s[:start]+'''  @Override public IngredientType<?> getType() { return TYPE; }
  @Override public boolean equals(Object other) {
    return other instanceof MaterialValueIngredient value && material.equals(value.material)
      && Float.compare(minValue,value.minValue)==0 && Float.compare(maxValue,value.maxValue)==0;
  }
  @Override public int hashCode() { return java.util.Objects.hash(material,minValue,maxValue); }
  public static final ResourceLocation ID = ResourceLocation.fromNamespaceAndPath("tconstruct","material_value");
  public static final MapCodec<MaterialValueIngredient> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
    MaterialIngredientFilter.CODEC.forGetter(value -> new MaterialIngredientFilter(value.material)),
    MaterialValueRange.CODEC.fieldOf("value").forGetter(value -> new MaterialValueRange(value.minValue,value.maxValue))
  ).apply(instance, (filter,range) -> new MaterialValueIngredient(filter.predicate(),range.min(),range.max())));
  public static final IngredientType<MaterialValueIngredient> TYPE = new IngredientType<>(CODEC);
}
'''
            s=s.replace('  private ItemStack[] items;\n','')
            s=s.replace('return minValue <= value && value <= maxValue &&', 'return Float.isFinite(value) && minValue <= value && value <= maxValue &&')
        path.write_text(s)
    changed=2
    for path in (root/'src/main/java').rglob('*.java'):
        s=path.read_text();before=s
        if path.name=='TinkerMaterials.java':
            s=s.replace('  void registerSerializers(RegisterEvent event) {','''  void registerSerializers(RegisterEvent event) {
    event.register(net.neoforged.neoforge.registries.NeoForgeRegistries.Keys.INGREDIENT_TYPES, helper -> {
      helper.register(MaterialIngredient.ID, MaterialIngredient.TYPE);
      helper.register(MaterialValueIngredient.ID, MaterialValueIngredient.TYPE);
    });''')
            for name in ('MaterialIngredient','MaterialValueIngredient'):
                s=re.sub(r'\s*CraftingHelper.register\('+name+r'\.Serializer.ID, '+name+r'\.Serializer.INSTANCE\);','',s)
        if path.name=='TinkerCommons.java':
            s=s.replace('  void registerRecipeSerializers(RegisterEvent event) {','''  void registerRecipeSerializers(RegisterEvent event) {
    event.register(net.neoforged.neoforge.registries.NeoForgeRegistries.Keys.INGREDIENT_TYPES,
      helper -> {
        helper.register(NoContainerIngredient.ID, NoContainerIngredient.TYPE);
        helper.register(BlockTagIngredient.ID, BlockTagIngredient.TYPE);
        helper.register(InstrumentIngredient.ID, InstrumentIngredient.TYPE);
      });''')
            s=s.replace('      CraftingHelper.register(NoContainerIngredient.ID, NoContainerIngredient.Serializer.INSTANCE);\n','')
            s=s.replace('      CraftingHelper.register(BlockTagIngredient.Serializer.ID, BlockTagIngredient.Serializer.INSTANCE);\n','')
            s=s.replace('      CraftingHelper.register(InstrumentIngredient.ID, InstrumentIngredient.SERIALIZER);\n','')
        if path.name=='TinkerTools.java':
            s=s.replace('  void registerRecipeSerializers(RegisterEvent event) {','''  void registerRecipeSerializers(RegisterEvent event) {
    event.register(net.neoforged.neoforge.registries.NeoForgeRegistries.Keys.INGREDIENT_TYPES,
      helper -> helper.register(ToolHookIngredient.ID, ToolHookIngredient.TYPE));''')
            s=re.sub(r'\s*CraftingHelper.register\(ToolHookIngredient.Serializer.ID, ToolHookIngredient.Serializer.INSTANCE\);','',s)
        if path.name=='SmelteryRecipeProvider.java':
            s=s.replace('new BlockTagIngredient(BlockTags.CONVERTABLE_TO_MUD)', 'new BlockTagIngredient(BlockTags.CONVERTABLE_TO_MUD).toVanilla()')
        if path.name=='ShapedMaterialRecipe.java':
            s=s.replace('ingredient instanceof MaterialValueIngredient', 'ingredient.getCustomIngredient() instanceof MaterialValueIngredient')
        if path.name=='ShapedMaterialExtension.java':
            s=s.replace('inputs.get(i) instanceof MaterialValueIngredient','inputs.get(i).getCustomIngredient() instanceof MaterialValueIngredient')
        if s!=before:path.write_text(s);changed+=1
    return {'consumer_files':changed,'ingredient_types':6}
