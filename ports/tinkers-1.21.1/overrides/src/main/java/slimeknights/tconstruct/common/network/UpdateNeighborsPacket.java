package slimeknights.tconstruct.common.network;

import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;

/** Client neighbor-shape updates after block replacement suppresses vanilla updates. */
public record UpdateNeighborsPacket(BlockState state, BlockPos pos) implements CustomPacketPayload {
  public static final Type<UpdateNeighborsPacket> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("tconstruct", "update_neighbors"));
  public static final StreamCodec<FriendlyByteBuf, UpdateNeighborsPacket> CODEC = StreamCodec.of(
    (buf, packet) -> { buf.writeVarInt(Block.getId(packet.state)); buf.writeBlockPos(packet.pos); },
    buf -> new UpdateNeighborsPacket(Block.stateById(buf.readVarInt()), buf.readBlockPos()));
  public UpdateNeighborsPacket { pos = pos.immutable(); }
  @Override public Type<UpdateNeighborsPacket> type() { return TYPE; }
  public void applyTo(Level level) {
    state.updateNeighbourShapes(level, pos, Block.UPDATE_CLIENTS, 511);
    state.updateIndirectNeighbourShapes(level, pos, Block.UPDATE_CLIENTS, 511);
  }
  public static void register(RegisterPayloadHandlersEvent event) {
    event.registrar("1").playToClient(TYPE, CODEC, (packet, context) -> packet.applyTo(context.player().level()));
  }
}
