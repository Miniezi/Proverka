package slimeknights.tconstruct.smeltery.capability;

import java.util.function.BiFunction;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.capabilities.BlockCapability;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.items.IItemHandler;

/** The controller's tank is private: external automation must use drains and ducts. */
public final class SmelteryCapabilities {
  private SmelteryCapabilities() {}
  public static final BlockCapability<IFluidHandler, Direction> INTERNAL_FLUID = BlockCapability.createSided(
    ResourceLocation.fromNamespaceAndPath("tconstruct", "smeltery_internal_fluid"), IFluidHandler.class);

  public static <BE extends BlockEntity> void registerFluid(RegisterCapabilitiesEvent event, BlockEntityType<BE> type,
                                                          BiFunction<BE, Direction, IFluidHandler> provider) {
    event.registerBlockEntity(Capabilities.FluidHandler.BLOCK, type, (entity, side) -> entity.isRemoved() ? null : provider.apply(entity, side));
  }
  public static <BE extends BlockEntity> void registerItem(RegisterCapabilitiesEvent event, BlockEntityType<BE> type,
                                                         BiFunction<BE, Direction, IItemHandler> provider) {
    event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, type, (entity, side) -> entity.isRemoved() ? null : provider.apply(entity, side));
  }
}
