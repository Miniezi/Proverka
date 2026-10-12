package ru.tconstructport;

import io.netty.buffer.Unpooled;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.common.network.UpdateNeighborsPacket;
import slimeknights.tconstruct.tools.network.EntityMovementChangePacket;

final class WorldPacketSmoke {
  static void init(IEventBus bus) { bus.addListener(UpdateNeighborsPacket::register); bus.addListener(EntityMovementChangePacket::register); }
  static void validate(ServerStartedEvent event) {
    var level=event.getServer().overworld();
    var pig=EntityType.PIG.create(level);
    if(pig==null || !level.addFreshEntity(pig)) throw new IllegalStateException("entity setup");
    try {
      pig.setDeltaMovement(1.25,-0.5,3.75);pig.setYRot(120f);pig.setXRot(-35f);
      var packet=new EntityMovementChangePacket(pig);
      var buffer=new FriendlyByteBuf(Unpooled.buffer());
      try {
        EntityMovementChangePacket.CODEC.encode(buffer,packet);
        var decoded=EntityMovementChangePacket.CODEC.decode(buffer);
        if(!packet.equals(decoded) || buffer.isReadable()) throw new IllegalStateException("movement roundtrip");
        pig.setDeltaMovement(0,0,0);pig.setYRot(0);pig.setXRot(0);
        decoded.applyTo(level);
        if(pig.getDeltaMovement().x!=1.25 || pig.getDeltaMovement().y!=-0.5 || pig.getDeltaMovement().z!=3.75 || pig.getYRot()!=120f || pig.getXRot()!=-35f) throw new IllegalStateException("movement application");
        new EntityMovementChangePacket(Integer.MAX_VALUE,0,0,0,0,0).applyTo(level);
      } finally {buffer.release();}
    } finally {pig.discard();}
    var pos=new BlockPos.MutableBlockPos(3,70,-4);
    var packet=new UpdateNeighborsPacket(Blocks.OAK_STAIRS.defaultBlockState(),pos);
    pos.set(0,0,0);
    var buffer=new FriendlyByteBuf(Unpooled.buffer());
    try {
      UpdateNeighborsPacket.CODEC.encode(buffer,packet);
      var decoded=UpdateNeighborsPacket.CODEC.decode(buffer);
      if(!decoded.equals(packet) || buffer.isReadable() || !decoded.pos().equals(new BlockPos(3,70,-4))) throw new IllegalStateException("block packet roundtrip or mutable position");
    } finally {buffer.release();}
    System.out.println("TCONSTRUCT_WORLD_PACKETS_OK codecs=2 movement=1 missing_entity=1 immutable_position=1");
  }
}
