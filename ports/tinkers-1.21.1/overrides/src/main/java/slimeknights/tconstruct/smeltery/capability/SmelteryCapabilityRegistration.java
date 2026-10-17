package slimeknights.tconstruct.smeltery.capability;

import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import slimeknights.tconstruct.smeltery.TinkerSmeltery;

@EventBusSubscriber(modid = "tconstruct", bus = EventBusSubscriber.Bus.MOD)
public final class SmelteryCapabilityRegistration {
  private SmelteryCapabilityRegistration() {}
  @SubscribeEvent
  public static void register(RegisterCapabilitiesEvent event) {
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.tank.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.fluidCannon.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.lantern.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.melter.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.alloyer.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.basin.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.table.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.castingTank.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.proxyTank.get(), (entity, side) -> entity.getFluidHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.drain.get(), (entity, side) -> entity.getForwardedHandler(side));
    SmelteryCapabilities.registerFluid(event, TinkerSmeltery.duct.get(), (entity, side) -> entity.getForwardedHandler(side));

    SmelteryCapabilities.registerItem(event, TinkerSmeltery.melter.get(), (entity, side) -> entity.getItemHandler());
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.heater.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.fluidCannon.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.basin.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.table.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.castingTank.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.proxyTank.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.duct.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.chute.get(), (entity, side) -> entity.getForwardedHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.smeltery.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    SmelteryCapabilities.registerItem(event, TinkerSmeltery.foundry.get(), (entity, side) -> entity.getAutomationItemHandler(side));
    event.registerBlockEntity(SmelteryCapabilities.INTERNAL_FLUID, TinkerSmeltery.smeltery.get(), (entity, side) -> entity.getFluidCapability());
    event.registerBlockEntity(SmelteryCapabilities.INTERNAL_FLUID, TinkerSmeltery.foundry.get(), (entity, side) -> entity.getFluidCapability());
  }
}
