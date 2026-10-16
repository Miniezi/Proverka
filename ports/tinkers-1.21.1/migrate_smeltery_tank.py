"""Port ordered smeltery fluid storage and component-aware merging/draining."""
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    p = base / 'tank/SmelteryTank.java'
    s = p.read_text()
    for old, new in [
        ('fluid.isFluidEqual(resource)', 'FluidStack.isSameFluidSameComponents(fluid, resource)'),
        ('fluid.isFluidEqual(toDrain)', 'FluidStack.isSameFluidSameComponents(fluid, toDrain)'),
        ('oldFirst.isFluidEqual(newFirst)', 'FluidStack.isSameFluidSameComponents(oldFirst, newFirst)')]:
        s = replace_once(s, old, new)
    s = replace_once(s, '    this.fluids.clear();\n    this.fluids.addAll(fluids);\n    contained = fluids.stream().mapToInt(FluidStack::getAmount).reduce(0, Integer::sum);',
                     '''    // Copy before clearing: packet lists and even our own list may be passed here.
    List<FluidStack> replacement = fluids.stream().filter(fluid -> !fluid.isEmpty()).map(FluidStack::copy).toList();
    this.fluids.clear();
    this.fluids.addAll(replacement);
    contained = replacement.stream().mapToInt(FluidStack::getAmount).reduce(0, Integer::sum);''')
    s = replace_once(s, 'public CompoundTag write(CompoundTag nbt)', 'public CompoundTag write(CompoundTag nbt, net.minecraft.core.HolderLookup.Provider registries)')
    s = replace_once(s, '      CompoundTag fluidTag = new CompoundTag();\n      liquid.writeToNBT(fluidTag);\n      list.add(fluidTag);',
                     '      if (!liquid.isEmpty()) list.add(liquid.save(registries));')
    s = replace_once(s, 'public void read(CompoundTag tag)', 'public void read(CompoundTag tag, net.minecraft.core.HolderLookup.Provider registries)')
    s = replace_once(s, 'FluidStack.loadFluidStackFromNBT(fluidTag)', 'FluidStack.parseOptional(registries, fluidTag)')
    s = replace_once(s, 'capacity = tag.getInt(TAG_CAPACITY);', 'capacity = Math.max(0, tag.getInt(TAG_CAPACITY));')
    p.write_text(s)
    p = base / 'controller/HeatingStructureBlockEntity.java'
    s = replace_once(p.read_text(), 'tank.read(nbt.getCompound(TAG_TANK))', 'tank.read(nbt.getCompound(TAG_TANK), registries)')
    s = replace_once(s, 'tank.write(new CompoundTag())', 'tank.write(new CompoundTag(), registries)')
    p.write_text(s)
    return {'classes': 2, 'component_sensitive_merge_and_drain': True, 'ordered_registry_storage': True}
