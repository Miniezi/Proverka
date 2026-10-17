"""Complete nested item-handler queries and persistence on the core fluid IO route."""
from migrate_nested_modifier_edits import replace_once
from migrate_smeltery_capabilities import replace_method


def migrate(root):
    base=root/'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    cap='net.neoforged.neoforge.capabilities.Capabilities.FluidHandler.ITEM'
    p=base/'tank/ProxyItemTank.java';s=p.read_text().replace('import net.neoforged.neoforge.common.capabilities.ForgeCapabilities;\n','')
    s=s.replace('stack.getCapability(ForgeCapabilities.FLUID_HANDLER_ITEM).isPresent()',f'stack.getCapability({cap}) != null')
    s=replace_method(s,'getItemTank',f'''  private IFluidHandlerItem getItemTank() {{
    ItemStack stack = getStack();
    IFluidHandlerItem current = stack.getCapability({cap});
    return current != null ? current : new EmptyFluidHandlerItem(stack);
  }}''')
    p.write_text(s)
    p=base/'inventory/DuctItemHandler.java';s=p.read_text().replace('import net.neoforged.neoforge.common.capabilities.ForgeCapabilities;\n','')
    s=replace_once(s,'''    return stack.getCapability(ForgeCapabilities.FLUID_HANDLER_ITEM)
                .filter(cap -> !cap.getFluidInTank(0).isEmpty())
                .isPresent();''',f'''    var handler = stack.getCapability({cap});
    return handler != null && handler.getTanks() > 0 && !handler.getFluidInTank(0).isEmpty();''')
    p.write_text(s)
    p=base/'inventory/DuctTankWrapper.java';s=p.read_text()
    s=replace_once(s,'    if (tankMapping == null) {','''    // A resolving parent can change tank count/order without changing this wrapper.
    {''')
    s=replace_once(s,'      int count = parent.getTanks();','      int count = parent.getTanks();\n      if (count <= 0) return new int[0];')
    s=s.replace('filter.isFluidEqual(contained)','FluidStack.isSameFluidSameComponents(filter, contained)')
    s=s.replace('itemHandler.getFluid().isFluidEqual(stack)','FluidStack.isSameFluidSameComponents(itemHandler.getFluid(), stack)')
    s=s.replace('itemHandler.getFluid().isFluidEqual(resource)','FluidStack.isSameFluidSameComponents(itemHandler.getFluid(), resource)')
    s=s.replace('new FluidStack(fluid, maxDrain)','fluid.copyWithAmount(maxDrain)')
    s=replace_once(s,'return FluidStack.isSameFluidSameComponents(itemHandler.getFluid(), stack);',
                     'return tank >= 0 && tank < getTanks() && !stack.isEmpty() && FluidStack.isSameFluidSameComponents(itemHandler.getFluid(), stack);')
    s=replace_once(s, 'private final DuctItemHandler itemHandler;', 'private final java.util.function.Supplier<FluidStack> filter;')
    s=replace_method(s, 'DuctTankWrapper', """  public DuctTankWrapper(IFluidHandler parent, java.util.function.Supplier<FluidStack> filter) {
    this.parent = parent;
    this.filter = filter;
  }""")
    s=s.replace('itemHandler.getFluid()', 'filter.get()')
    s=replace_method(s, 'getTankMapping', """  private int[] getTankMapping() {
    FluidStack selected = filter.get();
    int count = parent.getTanks();
    if (count <= 0) return new int[0];
    if (selected.isEmpty()) return parent.getFluidInTank(count - 1).isEmpty() ? new int[] {count - 1} : new int[0];
    IntList matching = new IntArrayList(count);
    for (int i = 0; i < count; i++) {
      FluidStack contained = parent.getFluidInTank(i);
      if (contained.isEmpty() || FluidStack.isSameFluidSameComponents(selected, contained)) matching.add(i);
    }
    return matching.toIntArray();
  }""")
    s=s.replace('    if (fluid.isEmpty()) {', '    if (maxDrain <= 0 || fluid.isEmpty()) {')
    p.write_text(s)
    p=base/'component/DuctBlockEntity.java'
    s=replace_once(p.read_text(), 'new DuctTankWrapper(capability, itemHandler)', 'new DuctTankWrapper(capability, itemHandler::getFluid)')
    p.write_text(s)
    for rel,field,key in [('ProxyTankBlockEntity.java','itemTank','TAG_ITEM'),('component/DuctBlockEntity.java','itemHandler','TAG_ITEM')]:
        p=base/rel;s=p.read_text()
        s=replace_once(s,f'{field}.readFromNBT(tags.getCompound({key}))' if 'Duct' in rel else f'{field}.readFromNBT(tag.getCompound({key}))',
                       f'{field}.readFromNBT(registries, tags.getCompound({key}))' if 'Duct' in rel else f'{field}.readFromNBT(registries, tag.getCompound({key}))')
        s=replace_once(s,f'{field}.writeToNBT()',f'{field}.writeToNBT(registries)')
        if 'Duct' in rel:
            s=replace_once(s,'public void handleUpdateTag(CompoundTag tag)', 'public void handleUpdateTag(CompoundTag tag, net.minecraft.core.HolderLookup.Provider registries)')
            s=replace_once(s,'super.handleUpdateTag(tag)','super.handleUpdateTag(tag, registries)')
        p.write_text(s)
    for rel in ['component/TankBlockEntity.java','CastingTankBlockEntity.java']:
        p=base/rel;s=p.read_text()
        s=replace_once(s,'public void updateTank(CompoundTag nbt)', 'public void updateTank(CompoundTag nbt, net.minecraft.core.HolderLookup.Provider registries)')
        s=replace_once(s,'tank.readFromNBT(nbt)','tank.readFromNBT(registries, nbt)')
        s=replace_once(s,'updateTank(tag.getCompound(NBTTags.TANK))','updateTank(tag.getCompound(NBTTags.TANK), registries)')
        s=replace_once(s,'tank.writeToNBT(new CompoundTag())','tank.writeToNBT(registries, new CompoundTag())')
        p.write_text(s)
    p=root/'src/main/java/slimeknights/tconstruct/smeltery/block/component/SearedTankBlock.java';s=p.read_text()
    s=replace_once(s,'tank.updateTank(nbt.getCompound(NBTTags.TANK))','tank.updateTank(nbt.getCompound(NBTTags.TANK), world.registryAccess())')
    p.write_text(s)
    for rel in ['module/SolidFuelModule.java','inventory/HeaterItemHandler.java']:
        p=base/rel;s=p.read_text().replace('CommonHooks.getBurnTime(stack, TinkerRecipeTypes.FUEL.get())','stack.getBurnTime(TinkerRecipeTypes.FUEL.get())');p.write_text(s)
    return {'nested_item_capabilities':True,'duct_dynamic_mapping':True,'inventory_and_tank_persistence':True}
