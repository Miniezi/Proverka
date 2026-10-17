package slimeknights.tconstruct.smeltery.capability;

import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;

/** Transfers an owned faucet buffer without discarding the portion an output refuses. */
public final class BufferedFluidTransfer {
  private BufferedFluidTransfer() {}
  public static int fillFromBuffer(IFluidHandler destination, FluidStack buffer, int limit) {
    if (buffer.isEmpty() || limit <= 0) return 0;
    int offered = Math.min(limit, buffer.getAmount());
    int simulated = destination.fill(buffer.copyWithAmount(offered), IFluidHandler.FluidAction.SIMULATE);
    int requested = Math.max(0, Math.min(offered, simulated));
    if (requested == 0) return 0;
    int filled = destination.fill(buffer.copyWithAmount(requested), IFluidHandler.FluidAction.EXECUTE);
    int accepted = Math.max(0, Math.min(requested, filled));
    buffer.shrink(accepted);
    return accepted;
  }
}
