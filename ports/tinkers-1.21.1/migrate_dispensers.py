"""Migrate dispenser source records, entity spawning and placed item components."""
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct'
    files = []
    for p in base.rglob('*.java'):
        s = p.read_text()
        if 'import net.minecraft.core.BlockSource;' not in s:
            continue
        s = s.replace('import net.minecraft.core.BlockSource;', 'import net.minecraft.core.dispenser.BlockSource;')
        for variable in ['source', 'pSource']:
            for old, new in [('getLevel()', 'level()'), ('getPos()', 'pos()'), ('getBlockState()', 'state()'), ('getEntity()', 'blockEntity()')]:
                s = s.replace(variable+'.'+old, variable+'.'+new)
        p.write_text(s)
        files.append(str(p.relative_to(base)))
    assert len(files) == 6, files
    p = base / 'gadgets/entity/DispenseFancyArmorStand.java'
    s = replace_once(p.read_text(), 'spawn(server, stack.getTag(), consumer, blockpos, MobSpawnType.DISPENSER, false, false)',
                     'spawn(server, consumer, blockpos, MobSpawnType.DISPENSER, false, false)')
    p.write_text(s)
    p = base / 'shared/block/PlaceBlockDispenserBehavior.java'
    s = p.read_text()
    start = s.index('    Level level = source.level();')
    end = s.index('    return stack;', start)
    s = s[:start] + '''    Level level = source.level();
    this.setSuccess(false);
    BlockPos target = source.pos().relative(source.state().getValue(DispenserBlock.FACING));
    if (level.isEmptyBlock(target) && stack.getItem() instanceof BlockItem blockItem) {
      Block block = blockItem.getBlock();
      BlockState state = block.defaultBlockState();
      if (level.setBlock(target, state, Block.UPDATE_ALL) && level.getBlockState(target).is(block)) {
        BlockItem.updateCustomBlockEntityTag(level, null, target, stack);
        var blockEntity = level.getBlockEntity(target);
        if (blockEntity != null) {
          blockEntity.applyComponentsFromItemStack(stack);
          blockEntity.setChanged();
        }
        block.setPlacedBy(level, target, state, null, stack);
        level.gameEvent(null, GameEvent.BLOCK_PLACE, target);
        SoundType sound = state.getSoundType(level, target, null);
        level.playSound(null, target, sound.getPlaceSound(), SoundSource.BLOCKS,
                        (sound.getVolume() + 1.0F) / 2.0F, sound.getPitch() * 0.8F);
        stack.shrink(1);
        this.setSuccess(true);
      }
    }
''' + s[end:]
    p.write_text(s)
    return {'source_record_files': files, 'placed_components': True, 'spawn_keeps_stack_config_consumer': True}
