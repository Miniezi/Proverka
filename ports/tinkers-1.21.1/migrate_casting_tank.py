"""Port the actual casting fluid handler and decouple callbacks for isolated execution."""
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    p = base / 'tank/CastingFluidHandler.java'
    s = p.read_text().replace('import lombok.RequiredArgsConstructor;\n', '').replace('@RequiredArgsConstructor\n', '')
    s = s.replace('import slimeknights.tconstruct.smeltery.block.entity.CastingBlockEntity;\n', '')
    s = replace_once(s, '  private final CastingBlockEntity tile;', '''  private final java.util.function.BiFunction<FluidStack,FluidAction,Integer> beginCasting;
  private final Runnable resetCasting;
  private final Runnable contentsChanged;

  public CastingFluidHandler(java.util.function.BiFunction<FluidStack,FluidAction,Integer> beginCasting,
                             Runnable resetCasting, Runnable contentsChanged) {
    this.beginCasting = beginCasting;
    this.resetCasting = resetCasting;
    this.contentsChanged = contentsChanged;
  }''')
    s = s.replace('tile.initNewCasting(resource, action)', 'beginCasting.apply(resource, action)')
    s = s.replace('tile.onContentsChanged()', 'contentsChanged.run()').replace('tile.reset()', 'resetCasting.run()')
    s = s.replace('new FluidStack(resource, amount)', 'resource.copyWithAmount(amount)').replace('new FluidStack(fluid, drained)', 'fluid.copyWithAmount(drained)')
    s = s.replace('resource.isFluidEqual(fluid)', 'FluidStack.isSameFluidSameComponents(resource, fluid)')
    s = replace_once(s, '    return getCapacity();\n  }\n\n  @Override\n  public boolean isFluidValid',
                     '    return tank == 0 ? getCapacity() : 0;\n  }\n\n  @Override\n  public boolean isFluidValid')
    start = s.index('  public void readFromTag(CompoundTag nbt) {')
    s = s[:start] + '''  public void readFromTag(CompoundTag nbt, net.minecraft.core.HolderLookup.Provider registries) {
    // Replacement load: missing keys must not retain the previous recipe's contents.
    reset();
    capacity = Math.max(0, nbt.getInt(TAG_CAPACITY));
    fluid = FluidStack.parseOptional(registries, nbt.getCompound(TAG_FLUID));
    ResourceLocation id = ResourceLocation.tryParse(nbt.getString(TAG_FILTER));
    if (id != null && BuiltInRegistries.FLUID.containsKey(id)) {
      filter = BuiltInRegistries.FLUID.get(id);
    }
  }

  public CompoundTag writeToTag(CompoundTag nbt, net.minecraft.core.HolderLookup.Provider registries) {
    nbt.putInt(TAG_CAPACITY, capacity);
    if (!fluid.isEmpty()) nbt.put(TAG_FLUID, fluid.save(registries));
    else nbt.remove(TAG_FLUID);
    if (filter != Fluids.EMPTY) nbt.putString(TAG_FILTER, BuiltInRegistries.FLUID.getKey(filter).toString());
    else nbt.remove(TAG_FILTER);
    return nbt;
  }
}
'''
    p.write_text(s)
    p = base / 'CastingBlockEntity.java'
    s = replace_once(p.read_text(), 'new CastingFluidHandler(this)', 'new CastingFluidHandler(this::initNewCasting, this::reset, this::onContentsChanged)')
    s = replace_once(s, 'tank.writeToTag(new CompoundTag())', 'tank.writeToTag(new CompoundTag(), registries)')
    s = replace_once(s, 'tank.readFromTag(tags.getCompound(TAG_TANK))', 'tank.readFromTag(tags.getCompound(TAG_TANK), registries)')
    p.write_text(s)
    return {'classes': 2, 'component_sensitive_transfer': True, 'registry_persistence': True}
