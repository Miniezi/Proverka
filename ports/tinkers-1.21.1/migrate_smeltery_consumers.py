"""Port faucet and fuel consumption to fresh world capability lookups."""
import re
from migrate_nested_modifier_edits import replace_once
from migrate_smeltery_capabilities import replace_method
LOOKUP='slimeknights.tconstruct.smeltery.capability.SmelteryHandlerLookup'


def optional_imports(s):
    s=s.replace('import net.neoforged.neoforge.common.util.LazyOptional;', 'import java.util.Optional;')
    for line in ['import net.neoforged.neoforge.common.capabilities.ForgeCapabilities;\n',
                 'import net.neoforged.neoforge.common.util.NonNullConsumer;\n',
                 'import slimeknights.mantle.util.WeakConsumerWrapper;\n']:
        s=s.replace(line,'')
    return s.replace('LazyOptional', 'Optional')


def migrate(root):
    base=root/'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    p=base/'FaucetBlockEntity.java';s=p.read_text()
    start=s.index('  /** Fluid handler of the input to the faucet */');end=s.index('  public FaucetBlockEntity(',start)
    s=s[:start]+s[end:]
    s=replace_method(s,'findFluidHandler',f'''  private Optional<IFluidHandler> findFluidHandler(Direction side) {{
    return {LOOKUP}.fluid(level, worldPosition.relative(side), side.getOpposite());
  }}''')
    s=replace_method(s,'getInputHandler','''  private Optional<IFluidHandler> getInputHandler() {
    return findFluidHandler(getBlockState().getValue(FACING).getOpposite());
  }''')
    s=replace_method(s,'getOutputHandler','''  private Optional<IFluidHandler> getOutputHandler() { return findFluidHandler(Direction.DOWN); }''')
    s=replace_method(s,'neighborChanged','''  public void neighborChanged(BlockPos neighbor) {
    // Handlers are resolved from the world at the point of use; no stale neighbor cache remains.
  }''')
    s=optional_imports(s)
    s=s.replace('renderFluid.isFluidEqual(drained)', 'FluidStack.isSameFluidSameComponents(renderFluid, drained)')
    s=s.replace('renderFluid.isFluidEqual(FluidStack.EMPTY)', 'FluidStack.isSameFluidSameComponents(renderFluid, FluidStack.EMPTY)')
    s=replace_once(s,'''        this.drained.shrink(filled);
        fillStack.setAmount(filled);
        output.fill(fillStack, IFluidHandler.FluidAction.EXECUTE);''', '''        slimeknights.tconstruct.smeltery.capability.BufferedFluidTransfer.fillFromBuffer(output, this.drained, filled);''')
    s=replace_once(s,'''      // output got lost. all liquid buffered is lost.
      reset();''','''      // Keep buffered liquid while the destination is absent; retry when it returns.
      // Removing the faucet still follows normal block removal behavior.''')
    for field in ['renderFluid','drained']:
        s=s.replace(f'{field}.writeToNBT(new CompoundTag())',f'{field}.save(registries)')
    s=s.replace('FluidStack.loadFluidStackFromNBT(compound.getCompound(TAG_DRAINED))','FluidStack.parseOptional(registries, compound.getCompound(TAG_DRAINED))')
    s=s.replace('FluidStack.loadFluidStackFromNBT(compound.getCompound(TAG_RENDER_FLUID))','FluidStack.parseOptional(registries, compound.getCompound(TAG_RENDER_FLUID))')
    p.write_text(s)
    p=base/'module/FuelModule.java';s=p.read_text()
    start=s.index('  /** Listener to attach to stored capability */');end=s.index('  /** Parent TE */',start);s=s[:start]+s[end:]
    s=replace_method(s,'resetHandler','''  protected void resetHandler(@Nullable Optional<?> source) { fluidHandler = null; }''')
    s=optional_imports(s).replace('new FluidStack(fluid, amount)','fluid.copyWithAmount(amount)')
    # Never grant heat when a nonconforming handler failed to supply the requested fuel.
    s=replace_once(s,'''          if (drained.getAmount() != amount) {
            TConstruct.LOG.error("Invalid amount of fuel drained from tank");
          }''','''          if (drained.getAmount() != amount || !FluidStack.isSameFluidSameComponents(drained, fluid)) {
            TConstruct.LOG.error("Invalid fuel drained from tank; refusing to grant heat");
            return 0;
          }''')
    p.write_text(s)
    p=base/'module/SolidFuelModule.java';s=p.read_text()
    start=s.index('  /** Listener to attach to stored item capabilities */');end=s.index('  /** Location of the fuel tank */',start);s=s[:start]+s[end:]
    s=replace_method(s,'resetHandler','''  @Override
  protected void resetHandler(@Nullable Optional<?> source) { itemHandler = null; fluidHandler = null; }''')
    s=replace_method(s,'fetchHandlers',f'''  private void fetchHandlers() {{
    fluidHandler = {LOOKUP}.fluid(getLevel(), fuelPos, null);
    itemHandler = {LOOKUP}.item(getLevel(), fuelPos, null);
  }}''')
    s=replace_once(s,'  public IFluidHandler getTank() {','  public IFluidHandler getTank() {\n    fetchHandlers();')
    p.write_text(optional_imports(s))
    p=base/'module/MultitankFuelModule.java';s=p.read_text()
    start=s.index('  /** Listener to attach to display capabilities */');end=s.index('  public MultitankFuelModule(',start);s=s[:start]+s[end:]
    s=replace_method(s,'resetHandler','''  @Override
  protected void resetHandler(@Nullable Optional<?> source) {
    if (source == null || source == fluidHandler) lastPos = NULL_POS;
    super.resetHandler(source);
  }''')
    s=replace_method(s,'clearFluidListeners','''  public void clearFluidListeners() { tankHandlers = null; fluidHandler = null; }''')
    s=replace_method(s,'ensureTankPresent','''  public void ensureTankPresent(BlockEntity be) { tankHandlers = null; }''')
    s=replace_method(s,'getTankHandlers',f'''  private Map<BlockPos,Optional<IFluidHandler>> getTankHandlers() {{
    Map<BlockPos,Optional<IFluidHandler>> current = new LinkedHashMap<>();
    Level world = getLevel();
    for (BlockPos pos : tankSupplier.get()) {{
      Optional<IFluidHandler> handler = {LOOKUP}.fluid(world, pos, null);
      if (handler.isPresent()) current.put(pos, handler);
    }}
    tankHandlers = current;
    return current;
  }}''')
    s=re.sub(r'^\s*\w+\.addListener\(fluidListener\);\n','\n',s,flags=re.M)
    s=optional_imports(s)
    for method in ['public int findFuel(boolean consume) {','public FuelInfo getFuelInfo() {','public FluidStack getLastFluid() {']:
        s=replace_once(s,method,method+'\n    fluidHandler = getTankHandlers().get(lastPos);')
    s=s.replace('getTank(tank).getFluidInTank(tank)','getTank(tank).getFluidInTank(0)').replace('getTank(tank).getTankCapacity(tank)','getTank(tank).getTankCapacity(0)')
    s=s.replace('currentFuel.isFluidEqual(fluid)','FluidStack.isSameFluidSameComponents(currentFuel, fluid)')
    s=s.replace('if (tankCap != fluidHandler)', 'if (fluidHandler == null || tankCap.orElse(null) != fluidHandler.orElse(null))')
    for old,new in [
      ('new FluidStack(resource, resource.getAmount() - filled)','resource.copyWithAmount(resource.getAmount() - filled)'),
      ('new FluidStack(resource, resource.getAmount() - drained.getAmount())','resource.copyWithAmount(resource.getAmount() - drained.getAmount())'),
      ('new FluidStack(drained, maxDrain - drained.getAmount())','drained.copyWithAmount(maxDrain - drained.getAmount())')]:s=s.replace(old,new)
    assert 'LazyOptional' not in s and 'addListener(' not in s
    p.write_text(s)
    return {'faucet':True,'fuel_modules':3,'world_queries_do_not_force_load':True}
