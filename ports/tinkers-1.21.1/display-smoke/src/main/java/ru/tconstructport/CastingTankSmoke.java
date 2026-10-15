package ru.tconstructport;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.smeltery.block.entity.tank.CastingFluidHandler;

final class CastingTankSmoke {
  static void validate(ServerStartedEvent event) {
    int[] changed = {0}, reset = {0};
    CastingFluidHandler[] owner = new CastingFluidHandler[1];
    var tank = new CastingFluidHandler((fluid, action) -> 1000,
      () -> { reset[0]++; owner[0].reset(); }, () -> changed[0]++);
    owner[0] = tank;
    var water = new FluidStack(Fluids.WATER, 1400);
    water.set(DataComponents.CUSTOM_NAME, Component.literal("molten test"));
    if (tank.fill(water, FluidAction.SIMULATE) != 1000 || !tank.isEmpty() || changed[0] != 0 || tank.getCapacity() != 0) fail("fill simulation mutated");
    if (tank.fill(water, FluidAction.EXECUTE) != 1000 || water.getAmount() != 1400 || tank.getFluid().getAmount() != 1000) fail("fill amount");
    var simulated = tank.drain(250, FluidAction.SIMULATE);
    if (simulated.getAmount() != 250 || tank.getFluid().getAmount() != 1000 || changed[0] != 1) fail("drain simulation");
    simulated.set(DataComponents.CUSTOM_NAME, Component.literal("mutated"));
    if (!tank.getFluid().get(DataComponents.CUSTOM_NAME).getString().equals("molten test")) fail("drain aliases");
    tank.drain(250, FluidAction.EXECUTE);
    if (tank.fill(new FluidStack(Fluids.LAVA, 100), FluidAction.EXECUTE) != 0
        || tank.fill(new FluidStack(Fluids.WATER, 100), FluidAction.EXECUTE) != 0) fail("mixed fluid/components accepted");
    var registries = event.getServer().registryAccess();
    var saved = tank.writeToTag(new CompoundTag(), registries);
    tank.reset(); tank.readFromTag(saved, registries);
    if (tank.getCapacity() != 1000 || tank.getFluid().getAmount() != 750
        || !FluidStack.isSameFluidSameComponents(tank.getFluid(), water)) fail("persistence");
    if (tank.drain(2000, FluidAction.EXECUTE).getAmount() != 750 || !tank.isEmpty() || reset[0] != 1) fail("empty reset");
    tank.readFromTag(saved, registries); tank.readFromTag(new CompoundTag(), registries);
    if (!tank.isEmpty() || tank.getCapacity() != 0 || tank.getTankCapacity(1) != 0) fail("replacement load");
    saved.putString("filter", "invalid id!"); saved.putInt("capacity", -1);
    tank.readFromTag(saved, registries);
    tank.reset(); tank.writeToTag(saved, registries);
    if (saved.contains("fluid") || saved.contains("filter")) fail("stale serialized fields");
    if (!tank.drain(-1, FluidAction.EXECUTE).isEmpty()) fail("negative drain");
    System.out.println("TCONSTRUCT_CASTING_TANK_OK simulation=1 transfer=1 components=1 persistence=1 reset=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
