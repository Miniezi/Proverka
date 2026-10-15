"""Port transparent blocks, beacon ARGB colors and concrete block codecs."""
from migrate_nested_modifier_edits import replace_once
import re


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct'
    for rel in ['shared/TinkerCommons.java', 'shared/block/SoulGlassBlock.java', 'shared/block/ClearStainedGlassBlock.java']:
        p = base / rel
        s = re.sub(r'\b(?:AbstractGlassBlock|GlassBlock)\b', 'TransparentBlock', p.read_text())
        p.write_text(s)
    for name in ['ClearStainedGlassBlock', 'ClearStainedGlassPaneBlock', 'SoulGlassBlock', 'BetterPaneBlock', 'ClearGlassPaneBlock']:
        p = base / f'shared/block/{name}.java'
        s = p.read_text()
        if name.startswith('ClearStained'):
            s = replace_once(s, 'public float[] getBeaconColorMultiplier(', 'public Integer getBeaconColorMultiplier(')
            s = replace_once(s, 'return this.glassColor.getRgb();', 'return 0xFF000000 | this.glassColor.getColor();')
            codec = f'''  public static final com.mojang.serialization.MapCodec<{name}> CODEC =
    com.mojang.serialization.codecs.RecordCodecBuilder.mapCodec(instance -> instance.group(
      propertiesCodec(),
      net.minecraft.util.StringRepresentable.fromEnum(GlassColor::values).fieldOf("color").forGetter(block -> block.glassColor)
    ).apply(instance, {name}::new));
'''
        else:
            codec = f'  public static final com.mojang.serialization.MapCodec<{name}> CODEC = simpleCodec({name}::new);\n'
        codec += f'''  @Override
  public com.mojang.serialization.MapCodec<? extends {name}> codec() {{ return CODEC; }}

'''
        marker = re.search(r'public class '+name+r'[^\n]+\{\n', s).group()
        s = replace_once(s, marker, marker + codec)
        if name == 'SoulGlassBlock':
            s = replace_once(s, 'isPathfindable(BlockState pState, BlockGetter pLevel, BlockPos pPos, PathComputationType pType)',
                             'isPathfindable(BlockState pState, PathComputationType pType)')
        p.write_text(s)
    return {'classes': 6, 'beacon_colors': 'ARGB', 'concrete_codecs': 5}
