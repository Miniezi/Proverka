package ru.tconstructport;
import io.netty.buffer.Unpooled;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.fluids.FluidStack;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import slimeknights.tconstruct.common.network.InventorySlotSyncPacket;
import slimeknights.tconstruct.smeltery.network.FluidUpdatePacket;

final class NetworkSmoke {
  static void init(IEventBus bus) { bus.addListener(NetworkSmoke::register); }
  private static void register(RegisterPayloadHandlersEvent event) {
    var registrar=event.registrar("1");
    registrar.playToClient(InventorySlotSyncPacket.TYPE,InventorySlotSyncPacket.CODEC,(p,c)->p.handle(c));
    registrar.playToClient(FluidUpdatePacket.TYPE,FluidUpdatePacket.CODEC,(p,c)->p.handle(c));
  }
  static void validate(ServerStartedEvent event) {
    var level=event.getServer().overworld();
    var item=new ItemStack(Items.DIAMOND_PICKAXE);
    item.set(DataComponents.CUSTOM_NAME,Component.literal("network component test"));
    item.setDamageValue(37);
    for(ItemStack input:new ItemStack[]{item,ItemStack.EMPTY}) {
      var packet=new InventorySlotSyncPacket(input,3,new BlockPos(2,70,3));
      var buf=new RegistryFriendlyByteBuf(Unpooled.buffer(),level.registryAccess());
      try {
        InventorySlotSyncPacket.CODEC.encode(buf,packet);
        var decoded=InventorySlotSyncPacket.CODEC.decode(buf);
        if(buf.isReadable() || !ItemStack.matches(input,decoded.itemStack()) || decoded.slot()!=3 || !decoded.pos().equals(packet.pos())) throw new IllegalStateException("item components roundtrip");
      } finally {buf.release();}
    }
    for(FluidStack input:new FluidStack[]{new FluidStack(Fluids.WATER,750),FluidStack.EMPTY}) {
      var packet=new FluidUpdatePacket(new BlockPos(-2,70,3),input);
      var buf=new RegistryFriendlyByteBuf(Unpooled.buffer(),level.registryAccess());
      try {
        FluidUpdatePacket.CODEC.encode(buf,packet);
        var decoded=FluidUpdatePacket.CODEC.decode(buf);
        final FluidStack[] received={null};
        decoded.handleBlockEntity(null,fluid->received[0]=fluid);
        if(buf.isReadable() || !FluidStack.matches(input,received[0]) || !decoded.pos().equals(packet.pos())) throw new IllegalStateException("fluid payload roundtrip");
      } finally {buf.release();}
    }
    System.out.println("TCONSTRUCT_NETWORK_CORE_OK item_components=1 empty_items=1 fluid=1 empty_fluid=1");
  }
}
