"""Migrate core smeltery providers and master forwarding to NeoForge block capabilities."""
import re
from migrate_nested_modifier_edits import replace_once

CAP='net.neoforged.neoforge.capabilities.Capabilities'
BASE='net.neoforged.neoforge.capabilities.BlockCapability'


def replace_method(s, name, replacement):
    pattern=re.compile(r'(?:  |\t)(?:@[^\n]+\n\s*)*(?:public|protected|private) [^\n{};=]*\b'+name+r'\([^)]*\)\s*\{')
    matches=list(pattern.finditer(s))
    assert len(matches)==1,(name,len(matches))
    m=matches[0];end=m.end();depth=1
    while depth:
        if s[end]=='{':depth+=1
        elif s[end]=='}':depth-=1
        end+=1
    return s[:m.start()]+replacement+s[end:]


def clean_imports(s):
    for n in ['Capability','ForgeCapabilities']:
        s=s.replace(f'import net.neoforged.neoforge.common.capabilities.{n};\n','')
    s=s.replace('import net.neoforged.neoforge.common.util.LazyOptional;\n','')
    return s


def migrate(root):
    base=root/'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    providers={
      'component/TankBlockEntity.java':('holder','tank'),
      'CastingBlockEntity.java':('holder','tank'),
      'controller/MelterBlockEntity.java':('tankHolder','tank'),
      'controller/AlloyerBlockEntity.java':('tankHolder','tank'),
      'CastingTankBlockEntity.java':('fluidHolder','tank'),
      'ProxyTankBlockEntity.java':('capability','itemTank'),
      'HeaterBlockEntity.java':('itemCapability',None),
      'FluidCannonBlockEntity.java':('itemCapability',None),
      'component/DuctBlockEntity.java':('itemCapability',None),
    }
    for rel,(holder,fluid) in providers.items():
        p=base/rel;s=p.read_text()
        s,n=re.subn(r'^\s*private final LazyOptional<[^\n]+\b'+holder+r'[^\n]*;\n','\n',s,flags=re.M);assert n==1,(rel,n)
        s=re.sub(r'^\s*(?:this\.)?'+holder+r' = LazyOptional\.of\([^\n]+;\n','\n',s,flags=re.M)
        if rel=='controller/MelterBlockEntity.java':
            s,n=re.subn(r'^\s*private final LazyOptional<IItemHandler> inventoryHolder[^\n]*;\n','\n',s,flags=re.M);assert n==1
        body=''
        if fluid: body+=f'  public net.neoforged.neoforge.fluids.capability.IFluidHandler getFluidHandler(@Nullable Direction side) {{ return {fluid}; }}\n'
        if rel in ['HeaterBlockEntity.java','FluidCannonBlockEntity.java','component/DuctBlockEntity.java']:
            body+='  public net.neoforged.neoforge.items.IItemHandler getAutomationItemHandler(@Nullable Direction side) { return itemHandler; }\n'
        if rel=='ProxyTankBlockEntity.java':
            body+='  public net.neoforged.neoforge.items.IItemHandler getAutomationItemHandler(@Nullable Direction side) { return itemTank; }\n'
        if rel=='CastingBlockEntity.java':
            # Mantle's old inventory capability was sided; retain the original sided view.
            body+='  public net.neoforged.neoforge.items.IItemHandler getAutomationItemHandler(@Nullable Direction side) { return side == null ? itemHandler : new net.neoforged.neoforge.items.wrapper.SidedInvWrapper(this, side); }\n'
        if rel=='CastingTankBlockEntity.java':
            body+='  public net.neoforged.neoforge.items.IItemHandler getAutomationItemHandler(@Nullable Direction side) { return side == null ? itemHandler : new net.neoforged.neoforge.items.wrapper.SidedInvWrapper(this, side); }\n'
        s=replace_method(s,'getCapability',body)
        if 'void invalidateCaps()' in s:s=replace_method(s,'invalidateCaps','')
        if rel=='component/DuctBlockEntity.java':
            s=replace_method(s,'makeWrapper','''  @Override
  protected IFluidHandler makeWrapper(IFluidHandler capability) {
    return new DuctTankWrapper(capability, itemHandler);
  }''')
        if rel=='CastingTankBlockEntity.java':
            s=s.replace('pStack.getCapability(ForgeCapabilities.FLUID_HANDLER_ITEM).isPresent()',f'pStack.getCapability({CAP}.FluidHandler.ITEM) != null')
        s=clean_imports(s)
        p.write_text(s)
    # Controller tank is private to drains; standard fluid capability stays unregistered.
    p=base/'controller/HeatingStructureBlockEntity.java';s=p.read_text()
    s=replace_once(s,'  @Getter\n  private LazyOptional<IFluidHandler> fluidCapability = LazyOptional.empty();','''  public IFluidHandler getFluidCapability() {
    return structure != null && !isRemoved() ? tank : null;
  }''')
    s=re.sub(r'^\s*private final LazyOptional<IItemHandler> itemCapability[^\n]*;\n','\n',s,flags=re.M)
    s=replace_method(s,'invalidateCaps','')
    s=replace_method(s,'getCapability','''  public IItemHandler getAutomationItemHandler(@Nullable Direction side) { return meltingInventory; }''')
    s=replace_once(s,'''      if (!fluidCapability.isPresent()) {
        fluidCapability = LazyOptional.of(() -> tank);
      }''','')
    s=replace_once(s,'''      if (fluidCapability.isPresent()) {
        fluidCapability.invalidate();
        fluidCapability = LazyOptional.empty();
      }''','')
    s=replace_once(s,'''      if (structure != null) {
        fluidCapability = LazyOptional.of(() -> tank);
      }''','')
    p.write_text(clean_imports(s))
    p=base/'tank/ISmelteryTankHandler.java';s=p.read_text().replace('import net.neoforged.neoforge.common.util.LazyOptional;\n','')
    s=replace_once(s,'LazyOptional<IFluidHandler> getFluidCapability();','@javax.annotation.Nullable IFluidHandler getFluidCapability();');p.write_text(s)
    # Master links expose stable resolving views. Cached consumers never retain a dead controller tank.
    p=base/'component/SmelteryInputOutputBlockEntity.java';s=p.read_text()
    s=s.replace('import net.neoforged.neoforge.common.util.NonNullConsumer;\n','').replace('import slimeknights.mantle.util.WeakConsumerWrapper;\n','')
    s=replace_once(s,'private final Capability<T> capability;',f'private final {BASE}<T,Direction> capability;')
    start=s.index('  /** Listener to attach to consumed capabilities */');end=s.index('  /* Retexturing */',start)
    s=s[:start]+'''  /** Stable view; each operation resolves the current master rather than retaining stale handlers. */
  private T forwardingHandler;

'''+s[end:]
    s=replace_once(s,'Capability<T> capability, T emptyInstance',f'{BASE}<T,Direction> capability, T emptyInstance')
    s=replace_method(s,'clearHandler','''  private void clearHandler() {
    // The view resolves its delegate for each operation; notify any external block caches as well.
    invalidateCapabilities();
  }''')
    s=replace_method(s,'invalidateCaps','')
    start=s.index('  /**\n   * Gets the capability to store in this IO block.');end=s.index('  /* Retexturing */',start)
    s=s[:start]+'''  @Nullable
  protected T resolveHandler() {
    if (level == null || isRemoved()) return null;
    BlockPos master = getMasterPos();
    if (master == null || master.equals(worldPosition) || !level.hasChunkAt(master)) return null;
    if (!validateMaster()) return null;
    return level.getCapability(capability, master, null);
  }

  protected abstract T makeForwardingHandler();

  public T getForwardedHandler(@Nullable Direction side) {
    if (forwardingHandler == null) forwardingHandler = makeForwardingHandler();
    return forwardingHandler;
  }

'''+s[end:]
    s=s.replace('ForgeCapabilities.FLUID_HANDLER','slimeknights.tconstruct.smeltery.capability.SmelteryCapabilities.INTERNAL_FLUID')
    s=s.replace('ForgeCapabilities.ITEM_HANDLER',CAP+'.ItemHandler.BLOCK')
    start=s.index('    /** Wraps the given capability */');end=s.index('\n  /** Item implementation',start)
    s=s[:start]+'''    protected IFluidHandler makeWrapper(IFluidHandler capability) { return capability; }

    @Override
    protected IFluidHandler makeForwardingHandler() {
      return makeWrapper(new slimeknights.tconstruct.smeltery.capability.ResolvingFluidHandler(this::resolveHandler));
    }
  }

'''+s[end:]
    pos=s.index('    public ChuteBlockEntity(BlockPos pos, BlockState state)')
    s=s[:pos]+'''    @Override
    protected IItemHandler makeForwardingHandler() {
      return new slimeknights.tconstruct.smeltery.capability.ResolvingItemHandler(this::resolveHandler);
    }

'''+s[pos:]
    p.write_text(clean_imports(s))
    return {'providers':9,'controller_private_fluid':True,'dynamic_master_forwarding':True}
