package ru.tconstructport;

import java.util.IdentityHashMap;
import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import io.netty.buffer.Unpooled;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.entity.FurnaceBlockEntity;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.fluids.capability.IFluidHandler.FluidAction;
import net.neoforged.neoforge.fluids.capability.templates.FluidTank;
import slimeknights.mantle.block.entity.MantleBlockEntity;
import slimeknights.tconstruct.library.recipe.fuel.*;
import slimeknights.tconstruct.library.recipe.ingredient.FluidIngredient;
import slimeknights.tconstruct.smeltery.block.entity.module.FuelModule;
import slimeknights.tconstruct.smeltery.block.entity.module.SolidFuelModule;
import slimeknights.tconstruct.smeltery.capability.SmelteryCapabilities;
import slimeknights.tconstruct.smeltery.capability.SmelteryHandlerLookup;

final class SmelteryFuelSmoke {
  private static final IdentityHashMap<BlockEntity,FluidTank> tanks = new IdentityHashMap<>();
  static void init(IEventBus bus) {
    SmelteryFuelRecipes.register(bus);
    bus.addListener(SmelteryFuelSmoke::registerCapabilities);
  }
  private static void registerCapabilities(RegisterCapabilitiesEvent event) {
    SmelteryCapabilities.registerFluid(event, BlockEntityType.BREWING_STAND,
      (entity, side) -> tanks.computeIfAbsent(entity, key -> new FluidTank(2000)));
  }
  static void validate(ServerStartedEvent event) {
    var level = event.getServer().overworld();
    var registries = level.registryAccess();
    var ops = registries.createSerializationContext(JsonOps.INSTANCE);
    var serializer = SmelteryFuelRecipes.SERIALIZER.get();
    var liquid = MeltingFuelLookup.findFuel(level, Fluids.LAVA);
    var solid = MeltingFuelLookup.getSolid(level);
    if (liquid == null || liquid.getAmount(Fluids.LAVA) != 50 || liquid.getDuration() != 100
        || liquid.getTemperature() != 1000 || liquid.getRate() != 10) fail("datapack liquid recipe load");
    if (solid == null || !solid.isSolid() || solid.getTemperature() != 800 || solid.getRate() != 8) fail("datapack solid recipe load");
    for (var fuel : java.util.List.of(liquid, solid)) {
      var json = serializer.codec().codec().encodeStart(ops, fuel).getOrThrow();
      var restored = serializer.codec().codec().parse(ops, json).getOrThrow();
      if (restored.isSolid() != fuel.isSolid() || restored.getRate() != fuel.getRate()) fail("native JSON roundtrip");
      var wire = new RegistryFriendlyByteBuf(Unpooled.buffer(), registries);
      try {
        serializer.streamCodec().encode(wire, fuel);
        var decoded = serializer.streamCodec().decode(wire);
        if (decoded.isSolid() != fuel.isSolid() || decoded.getTemperature() != fuel.getTemperature()
            || decoded.getDuration() != fuel.getDuration() || wire.isReadable()) fail("native recipe wire roundtrip");
      } finally { wire.release(); }
    }
    for (String invalid : new String[]{
      "{\"fluid\":{\"fluid\":\"minecraft:lava\",\"amount\":50},\"temperature\":1000,\"rate\":10}",
      "{\"temperature\":800,\"rate\":0}", "{\"temperature\":-1,\"rate\":8}"}) {
      if (serializer.codec().codec().parse(ops, JsonParser.parseString(invalid)).result().isPresent()) fail("invalid fuel JSON accepted");
    }
    var isolated = new RecipeManager(registries);
    var id = ResourceLocation.fromNamespaceAndPath("tconstruct", "fuel_reload_test");
    isolated.replaceRecipes(java.util.List.of(new RecipeHolder<>(id, liquid)));
    if (MeltingFuelLookup.findFuel(isolated, Fluids.LAVA) != liquid) fail("manager lookup");
    var replacement = new MeltingFuel(FluidIngredient.of(Fluids.LAVA, 75), 200, 1200, 12);
    isolated.replaceRecipes(java.util.List.of(new RecipeHolder<>(id, replacement)));
    if (MeltingFuelLookup.findFuel(isolated, Fluids.LAVA) != replacement || MeltingFuelLookup.findFuel(level, Fluids.LAVA) != liquid) fail("reload or world isolation");
    isolated.replaceRecipes(java.util.List.of());
    if (MeltingFuelLookup.findFuel(isolated, Fluids.LAVA) != null || MeltingFuelLookup.getSolid(isolated) != null) fail("removed recipe cached");

    var parentPos = new BlockPos(8, 200, 0);
    var fuelPos = parentPos.east();
    level.setBlockAndUpdate(parentPos, Blocks.DISPENSER.defaultBlockState());
    level.setBlockAndUpdate(fuelPos, Blocks.BREWING_STAND.defaultBlockState());
    var parent = new MantleBlockEntity(BlockEntityType.DISPENSER, parentPos, Blocks.DISPENSER.defaultBlockState());
    parent.setLevel(level);
    try {
      var source = (FluidTank)SmelteryHandlerLookup.fluid(level, fuelPos, null).orElseThrow();
      var lava = new FluidStack(Fluids.LAVA, 200);
      lava.set(DataComponents.CUSTOM_NAME, Component.literal("fuel components"));
      source.fill(lava, FluidAction.EXECUTE);
      var module = new SolidFuelModule(parent, fuelPos);
      if (module.findFuel(false) != 1000 || source.getFluidAmount() != 200 || module.getFuel() != 0) fail("fuel simulation consumed");
      if (module.findFuel(true) != 1000 || source.getFluidAmount() != 150 || module.getFuel() != 100
          || module.getRate() != 10 || module.getTemperature() != 1000) fail("liquid fuel execution");
      module.decreaseFuel(15);
      CompoundTag saved = module.writeToTag(new CompoundTag());
      var restored = new SolidFuelModule(parent, fuelPos);
      restored.readFromTag(saved);
      if (restored.getFuel() != 85 || restored.getFuelQuality() != 100 || restored.getRate() != 10 || restored.getTemperature() != 1000) fail("fuel progress persistence");
      restored.readFromTag(new CompoundTag());
      if (restored.getFuel() != 0 || restored.getRate() != 0 || restored.getTemperature() != 0) fail("empty fuel state did not replace");
      level.removeBlock(fuelPos, false);
      level.setBlockAndUpdate(fuelPos, Blocks.FURNACE.defaultBlockState());
      var furnace = (FurnaceBlockEntity)level.getBlockEntity(fuelPos);
      furnace.setItem(1, new ItemStack(Items.COAL, 2));
      var solidModule = new SolidFuelModule(parent, fuelPos);
      if (solidModule.findFuel(false) != 800 || furnace.getItem(1).getCount() != 2) fail("solid simulation");
      if (solidModule.findFuel(true) != 800 || furnace.getItem(1).getCount() != 1 || solidModule.getFuel() != 400
          || solidModule.getRate() != 8 || source.getFluidAmount() != 150) fail("solid fuel or stale fluid handler");
      var broken = new FluidTank(2000) {
        @Override public FluidStack drain(FluidStack resource, FluidAction action) { return FluidStack.EMPTY; }
      };
      broken.fill(lava, FluidAction.EXECUTE);
      var probe = new FuelModule(parent) {
        @Override public int findFuel(boolean consume) { return tryLiquidFuel(broken, consume); }
      };
      if (probe.findFuel(true) != 0 || probe.getFuel() != 0) fail("failed fuel extraction granted heat");
    } finally {
      level.removeBlock(fuelPos, false); level.removeBlock(parentPos, false); tanks.clear();
    }
    System.out.println("TCONSTRUCT_SMELTERY_FUEL_OK datapack=1 json=1 wire=1 reload=1 liquid=1 solid=1 persistence=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
