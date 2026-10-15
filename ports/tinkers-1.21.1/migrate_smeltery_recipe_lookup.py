"""Use manager-owned recipe holders/IDs for melting, casting and molding."""
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    p = base / 'module/MeltingModule.java'
    s = replace_once(p.read_text(), 'private IMeltingRecipe lastRecipe;', 'private net.minecraft.resources.ResourceLocation lastRecipeId;')
    start = s.index('    // first, try last recipe for the slot')
    end = s.index('\n  }', start)
    s = s[:start] + '''    var match = world.getRecipeManager().getRecipeFor(TinkerRecipeTypes.MELTING.get(), this, world, lastRecipeId);
    if (match.isPresent()) {
      lastRecipeId = match.get().id();
      return match.get().value();
    }
    lastRecipeId = null;
    return null;''' + s[end:]
    p.write_text(s)
    p = base / 'CastingBlockEntity.java'
    s = p.read_text().replace('import slimeknights.mantle.recipe.helper.RecipeHelper;\n', '')
    s = replace_once(s, 'private ICastingRecipe lastCastingRecipe;', 'private ResourceLocation lastCastingRecipeId;\n  private ResourceLocation currentRecipeId;')
    s = replace_once(s, 'private MoldingRecipe lastMoldingRecipe;', 'private ResourceLocation lastMoldingRecipeId;')
    for method, recipe, typ, inv, cache in [
        ('findCastingRecipe', 'ICastingRecipe', 'castingType', 'castingInventory', 'lastCastingRecipeId'),
        ('findMoldingRecipe', 'MoldingRecipe', 'moldingType', 'moldingInventory', 'lastMoldingRecipeId')]:
        start = s.index(f'  private {recipe} {method}() {{')
        end = s.index('\n  }', start) + len('\n  }')
        s = s[:start] + f'''  private {recipe} {method}() {{
    if (level == null) return null;
    var match = level.getRecipeManager().getRecipeFor({typ}, {inv}, level, {cache});
    if (match.isPresent()) {{
      {cache} = match.get().id();
      return match.get().value();
    }}
    {cache} = null;
    return null;
  }}''' + s[end:]
    assert s.count('this.currentRecipe = castingRecipe;') == 2
    s = s.replace('this.currentRecipe = castingRecipe;', 'this.currentRecipe = castingRecipe;\n          this.currentRecipeId = lastCastingRecipeId;')
    s = replace_once(s, 'currentRecipe = findCastingRecipe();', 'currentRecipe = findCastingRecipe();\n          currentRecipeId = lastCastingRecipeId;')
    s = replace_once(s, '    currentRecipe = null;', '    currentRecipe = null;\n    currentRecipeId = null;')
    s = replace_once(s, 'RecipeHelper.getRecipe(level.getRecipeManager(), name, ICastingRecipe.class).ifPresent(recipe -> {',
                     '''level.getRecipeManager().byKey(name)
        .filter(holder -> holder.value().getType() == castingType)
        .map(net.minecraft.world.item.crafting.RecipeHolder::value)
        .filter(ICastingRecipe.class::isInstance).map(ICastingRecipe.class::cast).ifPresent(recipe -> {''')
    s = replace_once(s, '        this.currentRecipe = recipe;', '        this.currentRecipe = recipe;\n        this.currentRecipeId = name;')
    s = replace_once(s, '      tags.putString(TAG_RECIPE, currentRecipe.getId().toString());',
                     '      if (currentRecipeId != null) tags.putString(TAG_RECIPE, currentRecipeId.toString());')
    # Loading replaces previous active recipe state, even when the saved recipe was removed.
    s = replace_once(s, '    FluidStack fluid = tank.getFluid();\n    if(!fluid.isEmpty()) {',
                     '    currentRecipe = null;\n    currentRecipeId = null;\n    FluidStack fluid = tank.getFluid();\n    if(!fluid.isEmpty()) {')
    p.write_text(s)
    return {'classes': 2, 'manager_owned_recipe_ids': True, 'lookup_modes': ['melting', 'casting', 'molding']}
