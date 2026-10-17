package ru.tconstructport;

import java.util.IdentityHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.capabilities.BlockCapabilityCache;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import net.neoforged.neoforge.items.ItemStackHandler;
import slimeknights.tconstruct.smeltery.capability.*;

/** Vanilla fixture block entities exercise the real registration and resolving-view infrastructure. */
final class SmelteryCapabilitySmoke {
  private static final IdentityHashMap<BlockEntity,FluidTank> tanks = new IdentityHashMap<>();
  static void init(IEventBus bus) { bus.addListener(SmelteryCapabilitySmoke::register); }
  private static void register(RegisterCapabilitiesEvent event) {
    SmelteryCapabilities.registerFluid(event, BlockEntityType.DISPENSER,
      (entity, side) -> side == Direction.NORTH ? tanks.computeIfAbsent(entity, key -> new FluidTank(2000)) : null);
  }
  static void validate(ServerStartedEvent event) {
    var level = event.getServer().overworld();
    var pos = new BlockPos(4, 200, 4);
    level.setBlockAndUpdate(pos, Blocks.DISPENSER.defaultBlockState());
    try {
      var initial = SmelteryHandlerLookup.fluid(level, pos, Direction.NORTH).orElseThrow();
      if (SmelteryHandlerLookup.fluid(level, pos, Direction.SOUTH).isPresent()
          || level.getCapability(SmelteryCapabilities.INTERNAL_FLUID, pos, Direction.NORTH) != null) fail("side or private capability");
      var relay = new ResolvingFluidHandler(() -> SmelteryHandlerLookup.fluid(level, pos, Direction.NORTH).orElse(null));
      var water = new FluidStack(Fluids.WATER, 500);
      water.set(DataComponents.CUSTOM_NAME, Component.literal("core fluid"));
      if (relay.fill(water, IFluidHandler.FluidAction.SIMULATE) != 500 || initial.getFluidInTank(0).getAmount() != 0) fail("simulation");
      if (relay.fill(water, IFluidHandler.FluidAction.EXECUTE) != 500 || water.getAmount() != 500) fail("forward fill");
      var cache = BlockCapabilityCache.create(Capabilities.FluidHandler.BLOCK, level, pos, Direction.NORTH);
      if (cache.getCapability() != initial) fail("cached provider");
      level.removeBlock(pos, false);
      if (cache.getCapability() != null || !relay.drain(100, IFluidHandler.FluidAction.EXECUTE).isEmpty()) fail("removed target remains accessible");
      level.setBlockAndUpdate(pos, Blocks.DISPENSER.defaultBlockState());
      var replacement = SmelteryHandlerLookup.fluid(level, pos, Direction.NORTH).orElseThrow();
      if (replacement == initial || !relay.drain(100, IFluidHandler.FluidAction.EXECUTE).isEmpty()) fail("stale target after replacement");
      if (relay.fill(water, IFluidHandler.FluidAction.EXECUTE) != 500 || initial.getFluidInTank(0).getAmount() != 500) fail("replacement routing");
      var restored = relay.drain(100, IFluidHandler.FluidAction.EXECUTE);
      if (restored.getAmount() != 100 || !FluidStack.isSameFluidSameComponents(restored, water)) fail("component forwarding");
    } finally { level.removeBlock(pos, false); tanks.clear(); }
    var first = new ItemStackHandler(1);
    var second = new ItemStackHandler(1);
    net.neoforged.neoforge.items.IItemHandler[] active = {first};
    var itemRelay = new ResolvingItemHandler(() -> active[0]);
    itemRelay.insertItem(0, new ItemStack(Items.IRON_INGOT, 3), false);
    active[0] = second;
    if (!itemRelay.extractItem(0, 1, false).isEmpty() || first.getStackInSlot(0).getCount() != 3) fail("stale item target");
    active[0] = null;
    if (itemRelay.insertItem(0, new ItemStack(Items.GOLD_INGOT), false).getCount() != 1) fail("missing item target loses items");
    var buffer = new FluidStack(Fluids.WATER, 100);
    buffer.set(DataComponents.CUSTOM_NAME, Component.literal("buffer"));
    var partial = new FluidTank(1000) {
      @Override public int fill(FluidStack resource, FluidAction action) {
        return super.fill(resource.copyWithAmount(action.execute() ? Math.min(37, resource.getAmount()) : resource.getAmount()), action);
      }
    };
    if (BufferedFluidTransfer.fillFromBuffer(partial, buffer, 100) != 37 || buffer.getAmount() != 63 || partial.getFluidAmount() != 37) fail("partial execution loses fluid");
    if (!FluidStack.isSameFluidSameComponents(buffer, partial.getFluid())) fail("buffer components lost");
    if (BufferedFluidTransfer.fillFromBuffer(partial, buffer, -1) != 0 || buffer.getAmount() != 63) fail("invalid transfer limit");
    System.out.println("TCONSTRUCT_SMELTERY_CAPABILITIES_OK registration=1 sides=1 invalidation=1 replacement=1 forwarding=1 conservation=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
