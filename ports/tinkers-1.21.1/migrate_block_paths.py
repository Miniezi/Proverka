"""Port pathfinding signatures and codecs for the seared component hierarchy."""
import re
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct'
    paths = []
    signatures = 0
    for p in base.rglob('*.java'):
        s = p.read_text()
        old = s
        s = re.sub(r'\bBlockPathTypes\b', 'PathType', s)
        pattern = r'public boolean isPathfindable\(BlockState (\w+), BlockGetter (\w+), BlockPos (\w+), PathComputationType (\w+)\) \{\s*return false;\s*\}'
        s, n = re.subn(pattern, lambda m: f'public boolean isPathfindable(BlockState {m[1]}, PathComputationType {m[4]}) {{\n    return false;\n  }}', s)
        signatures += n
        if s != old:
            paths.append(str(p.relative_to(base)))
            p.write_text(s)
    # The glass migration has already converted SoulGlassBlock; six remain.
    assert signatures == 6, signatures
    for name in ['SearedBlock', 'SearedGlassBlock', 'SearedTintedGlassBlock', 'SearedSoulGlassBlock']:
        p = base / f'smeltery/block/component/{name}.java'
        s = p.read_text()
        if name == 'SearedBlock':
            codec = '''  public static final com.mojang.serialization.MapCodec<SearedBlock> CODEC =
    com.mojang.serialization.codecs.RecordCodecBuilder.mapCodec(instance -> instance.group(
      propertiesCodec(),
      com.mojang.serialization.Codec.BOOL.fieldOf("required_block_entity").forGetter(block -> block.requiredBlockEntity)
    ).apply(instance, SearedBlock::new));
'''
        else:
            codec = f'  public static final com.mojang.serialization.MapCodec<{name}> CODEC = simpleCodec({name}::new);\n'
        codec += f'''  @Override
  public com.mojang.serialization.MapCodec<? extends {name}> codec() {{ return CODEC; }}

'''
        marker = re.search(r'public class '+name+r'[^\n]+\{\n', s).group()
        p.write_text(replace_once(s, marker, marker + codec))
    return {'path_files': paths, 'path_signatures': signatures, 'seared_codecs': 4}
