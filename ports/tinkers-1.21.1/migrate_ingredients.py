"""Keep TConstruct's quantity-sensitive recipe formats on Mantle 1.21.

NeoForge's native sized ingredients have different JSON keys, empty semantics,
and cannot represent alternative fluids with different required quantities.
The relocated, MIT-licensed implementations preserve the existing data format.
"""
import re

def migrate(root):
    changed = 0
    fluid_objects = 0
    for path in (root / 'src/main/java').rglob('*.java'):
        original = path.read_text()
        source = original
        for name in ('SizedIngredient', 'FluidIngredient'):
            source = source.replace('slimeknights.mantle.recipe.ingredient.' + name,
                                    'slimeknights.tconstruct.library.recipe.ingredient.' + name)
        if 'import slimeknights.tconstruct.library.recipe.ingredient.FluidIngredient;' in source:
            # All nonempty ingredient(...) receivers in these files are Mantle
            # FluidObjects; zero-argument recipe ingredient accessors stay intact.
            source, number = re.subn(r'\b(TinkerFluids\.\w+|fluidObject|fluid)\.ingredient\((?=\s*[^\s)])',
                                     r'FluidIngredient.of(\1, ', source)
            fluid_objects += number
        if source != original:
            path.write_text(source)
            changed += 1
    return {'files': changed, 'fluid_object_factories': fluid_objects}
