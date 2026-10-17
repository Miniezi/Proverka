package slimeknights.tconstruct.smeltery.capability;

import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.items.IItemHandler;

/** Current world capability lookup. Never force-load a neighbor chunk or retain removed block entities. */
public final class SmelteryHandlerLookup {
  private SmelteryHandlerLookup() {}
  public static Optional<IFluidHandler> fluid(Level level, BlockPos pos, Direction side) {
    return level == null || !level.hasChunkAt(pos) ? Optional.empty()
      : Optional.ofNullable(level.getCapability(Capabilities.FluidHandler.BLOCK, pos, side));
  }
  public static Optional<IItemHandler> item(Level level, BlockPos pos, Direction side) {
    return level == null || !level.hasChunkAt(pos) ? Optional.empty()
      : Optional.ofNullable(level.getCapability(Capabilities.ItemHandler.BLOCK, pos, side));
  }
}
