"""Native fuel recipe codecs, world-owned lookup, datagen and fuel execution context."""
import re
import json
from migrate_nested_modifier_edits import replace_once
from migrate_smeltery_capabilities import replace_method


def migrate(root):
    base=root/'src/main/java/slimeknights/tconstruct'
    p=base/'library/recipe/TinkerRecipeTypes.java';s=p.read_text()
    s=replace_once(s,'RecipeType<MeltingFuel>> FUEL = register("fuel");', 'RecipeType<MeltingFuel>> FUEL = slimeknights.tconstruct.library.recipe.fuel.SmelteryFuelRecipes.TYPE;')
    s=replace_once(s,'    TYPES.register(bus);','    TYPES.register(bus);\n    slimeknights.tconstruct.library.recipe.fuel.SmelteryFuelRecipes.register(bus);')
    p.write_text(s)
    p=base/'smeltery/TinkerSmeltery.java';s=p.read_text()
    s=replace_once(s,'fuelSerializer = RECIPE_SERIALIZERS.register("melting_fuel", () -> LoadableRecipeSerializer.of(MeltingFuel.LOADER));',
                     'fuelSerializer = slimeknights.tconstruct.library.recipe.fuel.SmelteryFuelRecipes.SERIALIZER;')
    p.write_text(s)
    p=base/'smeltery/block/entity/module/FuelModule.java';s=p.read_text()
    s=s.replace('import slimeknights.tconstruct.TConstruct;\n','').replace('import slimeknights.tconstruct.library.utils.Util;\n','')
    s=s.replace('TConstruct.LOG.error(', 'com.mojang.logging.LogUtils.getLogger().error(')
    s=replace_method(s,'findRecipe','''  @Nullable
  protected MeltingFuel findRecipe(Fluid fluid) {
    return MeltingFuelLookup.findFuel(getLevel(), fluid);
  }''')
    # A loaded empty compound replaces old progress rather than keeping stale heat.
    s=replace_method(s,'readFromTag','''  public void readFromTag(CompoundTag nbt) {
    fuel = Math.max(0, nbt.getInt(TAG_FUEL));
    fuelQuality = nbt.contains("fuel_quality", Tag.TAG_ANY_NUMERIC) ? Math.max(0, nbt.getInt("fuel_quality")) : fuel;
    temperature = Math.max(0, nbt.getInt(TAG_TEMPERATURE));
    rate = Math.max(0, nbt.getInt(TAG_RATE));
    fluidHandler = null;
  }''')
    s=replace_once(s,'    nbt.putInt(TAG_FUEL, fuel);','    nbt.putInt(TAG_FUEL, fuel);\n    nbt.putInt("fuel_quality", fuelQuality);')
    p.write_text(s)
    p=base/'smeltery/block/entity/module/SolidFuelModule.java';s=p.read_text()
    s=s.replace('import slimeknights.tconstruct.TConstruct;\n','').replace('import slimeknights.tconstruct.library.utils.Util;\n','').replace('import slimeknights.tconstruct.library.recipe.TinkerRecipeTypes;\n','')
    s=s.replace('TConstruct.LOG.error(', 'com.mojang.logging.LogUtils.getLogger().error(')
    s=s.replace('TinkerRecipeTypes.FUEL.get()', 'slimeknights.tconstruct.library.recipe.fuel.SmelteryFuelRecipes.TYPE.get()')
    s=replace_once(s,'MeltingFuel solid = MeltingFuelLookup.getSolid();','MeltingFuel solid = MeltingFuelLookup.getSolid(getLevel());\n        if (solid == null) return 0;')
    p.write_text(s)
    p=base/'tools/modules/OverburnModule.java';s=replace_once(p.read_text(),'MeltingFuelLookup.findFuel(fluid.getFluid())','MeltingFuelLookup.findFuel(world, fluid.getFluid())');p.write_text(s)
    p=base/'plugin/jei/melting/MeltingCategory.java';s=p.read_text()
    s=replace_once(s,'MeltingFuel solid = MeltingFuelLookup.getSolid();','MeltingFuel solid = MeltingFuelLookup.getSolid();\n    if (solid == null) return;')
    s=replace_once(s,'if (recipe.getTemperature() <= MeltingFuelLookup.getSolid().getTemperature()) {','MeltingFuel solid = MeltingFuelLookup.getSolid();\n    if (solid != null && recipe.getTemperature() <= solid.getTemperature()) {')
    p.write_text(s)
    p=base/'library/recipe/fuel/MeltingFuelBuilder.java';s=p.read_text()
    s=s.replace('import net.minecraft.data.recipes.FinishedRecipe;','import net.minecraft.data.recipes.RecipeOutput;')
    s=s.replace('Consumer<FinishedRecipe> consumer','RecipeOutput consumer')
    s=replace_once(s,'ResourceLocation advancementId = this.buildOptionalAdvancement(id, "melting_fuel");','var advancement = this.buildOptionalAdvancement(consumer, id, "melting_fuel");')
    s=replace_once(s,'consumer.accept(new LoadableFinishedRecipe<>(new MeltingFuel(id, input, duration, temperature, rate), MeltingFuel.LOADER, advancementId));',
                     'consumer.accept(id, new MeltingFuel(input, duration, temperature, rate), advancement);')
    p.write_text(s)
    resources = []
    for folder in [root/'src/main/resources', root/'src/generated/resources']:
        if not folder.exists(): continue
        for recipe in list(folder.glob('data/*/recipes/**/*.json')):
            if json.loads(recipe.read_text()).get('type') != 'tconstruct:melting_fuel': continue
            parts = list(recipe.relative_to(folder).parts)
            parts[2] = 'recipe'
            target = folder.joinpath(*parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            assert not target.exists(), target
            recipe.rename(target)
            resources.append(str(target.relative_to(root)))
    return {'world_owned_fuel_lookup':True,'native_recipe_serializer':True,'recipe_output_builder':True,'fuel_progress_persistence':True,'native_fuel_resources':resources}
