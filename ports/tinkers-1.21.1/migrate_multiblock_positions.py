"""Keep controller/servant links and fuel positions readable after 1.21 NBT changes."""
from migrate_nested_modifier_edits import replace_once
from migrate_smeltery_capabilities import replace_method
READ='slimeknights.tconstruct.common.multiblock.MultiblockPositionData.read'


def migrate(root):
    base=root/'src/main/java/slimeknights/tconstruct'
    p=base/'library/utils/TagUtil.java';s=p.read_text()
    s=replace_method(s,'readOptionalPos',f'''  @Nullable
  public static BlockPos readOptionalPos(CompoundTag parent, String key, BlockPos offset) {{
    BlockPos relative = {READ}(parent.get(key));
    return relative == null ? null : relative.offset(offset);
  }}''')
    p.write_text(s)
    p=base/'common/multiblock/ServantTileEntity.java';s=p.read_text()
    s=replace_once(s,'public void load(CompoundTag tags)', 'public void loadAdditional(CompoundTag tags, net.minecraft.core.HolderLookup.Provider registries)')
    s=replace_once(s,'super.load(tags)','super.loadAdditional(tags, registries)')
    s=replace_once(s,'public void saveAdditional(CompoundTag tags)','public void saveAdditional(CompoundTag tags, net.minecraft.core.HolderLookup.Provider registries)')
    s=replace_once(s,'super.saveAdditional(tags)','super.saveAdditional(tags, registries)')
    s=replace_once(s,'''      this.masterBlock = masterBlock;
    }
  }

  @Override
  public void loadAdditional''','''      this.masterBlock = masterBlock;
    } else {
      this.masterPos = null;
      this.masterBlock = null;
    }
  }

  @Override
  public void loadAdditional''')
    p.write_text(s)
    p=base/'smeltery/block/entity/multiblock/MultiblockCuboid.java';s=p.read_text()
    s=replace_once(s,'ListTag list = rootTag.getList(key, Tag.TAG_COMPOUND);','Tag raw = rootTag.get(key);\n    if (!(raw instanceof ListTag list)) return Collections.emptyList();')
    s=replace_once(s,'BlockPos pos = NbtUtils.readBlockPos(list.getCompound(i));',f'BlockPos pos = {READ}(list.get(i));')
    s=replace_once(s,'if (!pos.equals(BlockPos.ZERO)) {','if (pos != null && !pos.equals(BlockPos.ZERO)) {')
    p.write_text(s)
    p=base/'smeltery/block/entity/module/MultitankFuelModule.java';s=p.read_text()
    s=replace_once(s,'''    if (nbt.contains(TAG_LAST_FUEL, Tag.TAG_COMPOUND)) {
      lastPos = NbtUtils.readBlockPos(nbt.getCompound(TAG_LAST_FUEL)).offset(parent.getBlockPos());
    }''',f'''    BlockPos relative = {READ}(nbt.get(TAG_LAST_FUEL));
    lastPos = relative == null ? NULL_POS : relative.offset(parent.getBlockPos());
    fluidHandler = null;''')
    p.write_text(s)
    p=base/'smeltery/block/entity/controller/HeatingStructureBlockEntity.java';s=p.read_text()
    s=replace_once(s,'''    if (nbt.contains(TAG_ERROR_POS, Tag.TAG_COMPOUND)) {
      this.errorPos = NbtUtils.readBlockPos(nbt.getCompound(TAG_ERROR_POS)).offset(this.worldPosition);
    }''',f'''    BlockPos relativeError = {READ}(nbt.get(TAG_ERROR_POS));
    if (relativeError != null) this.errorPos = relativeError.offset(this.worldPosition);''')
    p.write_text(s)
    p=base/'smeltery/block/entity/tank/ProxyItemTank.java';s=p.read_text().replace('ItemStack.isSameItemSameTags(oldStack, newStack)','ItemStack.isSameItemSameComponents(oldStack, newStack)');p.write_text(s)
    return {'classes':6,'native_and_legacy_position_read':True,'servant_registry_lifecycle':True}
