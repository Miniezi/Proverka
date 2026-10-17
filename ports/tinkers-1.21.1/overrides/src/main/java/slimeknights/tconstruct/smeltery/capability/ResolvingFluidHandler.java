package slimeknights.tconstruct.smeltery.capability;

import java.util.function.Supplier;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.EmptyFluidHandler;

/** Stable automation view whose delegate may disappear or change with a multiblock. */
public final class ResolvingFluidHandler implements IFluidHandler {
  private final Supplier<IFluidHandler> resolve;
  public ResolvingFluidHandler(Supplier<IFluidHandler> resolve) { this.resolve = resolve; }
  private IFluidHandler handler() {
    IFluidHandler current = resolve.get();
    return current == null || current == this ? EmptyFluidHandler.INSTANCE : current;
  }
  @Override public int getTanks() { return handler().getTanks(); }
  @Override public FluidStack getFluidInTank(int tank) { return handler().getFluidInTank(tank); }
  @Override public int getTankCapacity(int tank) { return handler().getTankCapacity(tank); }
  @Override public boolean isFluidValid(int tank, FluidStack stack) { return handler().isFluidValid(tank, stack); }
  @Override public int fill(FluidStack resource, FluidAction action) { return handler().fill(resource, action); }
  @Override public FluidStack drain(FluidStack resource, FluidAction action) { return handler().drain(resource, action); }
  @Override public FluidStack drain(int maxDrain, FluidAction action) { return handler().drain(maxDrain, action); }
}
