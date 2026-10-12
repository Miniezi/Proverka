package slimeknights.tconstruct.common.network;
import net.minecraft.core.BlockPos;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.players.PlayerList;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.ChunkPos;
import net.neoforged.neoforge.network.PacketDistributor;
import javax.annotation.Nullable;

/** NeoForge transport retaining the existing call-site order and recipient scope. */
public class TinkerPacketSender {
  public void sendTo(CustomPacketPayload message, Entity player) {
    if (player instanceof ServerPlayer serverPlayer) PacketDistributor.sendToPlayer(serverPlayer, message);
  }
  public void sendToServer(CustomPacketPayload message) { PacketDistributor.sendToServer(message); }
  public void sendVanillaPacket(Entity player, Packet<?> packet) {
    if (player instanceof ServerPlayer serverPlayer) serverPlayer.connection.send(packet);
  }
  public void sendToClientsAround(CustomPacketPayload message, @Nullable LevelAccessor level, BlockPos pos) {
    if (level instanceof ServerLevel server) PacketDistributor.sendToPlayersTrackingChunk(server, new ChunkPos(pos), message);
  }
  public void sendToTracking(CustomPacketPayload message, Entity entity) { PacketDistributor.sendToPlayersTrackingEntity(entity, message); }
  public void sendToTrackingAndSelf(CustomPacketPayload message, Entity entity) { PacketDistributor.sendToPlayersTrackingEntityAndSelf(entity, message); }
  public void sendToPlayerList(@Nullable ServerPlayer target, PlayerList players, CustomPacketPayload message) {
    if (target != null) sendTo(message,target);
    else for (ServerPlayer player : players.getPlayers()) sendTo(message,player);
  }
}
