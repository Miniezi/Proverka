package slimeknights.tconstruct.tools.network;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;

/** Clientbound entity velocity and rotation update, resolved in the receiving world. */
public record EntityMovementChangePacket(int entityID, double x, double y, double z, float yRot, float xRot) implements CustomPacketPayload {
  public static final Type<EntityMovementChangePacket> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("tconstruct", "entity_movement"));
  public static final StreamCodec<FriendlyByteBuf, EntityMovementChangePacket> CODEC = StreamCodec.of(
    (buf, packet) -> { buf.writeInt(packet.entityID); buf.writeDouble(packet.x); buf.writeDouble(packet.y); buf.writeDouble(packet.z); buf.writeFloat(packet.yRot); buf.writeFloat(packet.xRot); },
    buf -> new EntityMovementChangePacket(buf.readInt(), buf.readDouble(), buf.readDouble(), buf.readDouble(), buf.readFloat(), buf.readFloat()));
  public EntityMovementChangePacket(Entity entity) {
    this(entity.getId(), entity.getDeltaMovement().x, entity.getDeltaMovement().y, entity.getDeltaMovement().z, entity.getYRot(), entity.getXRot());
  }
  @Override public Type<EntityMovementChangePacket> type() { return TYPE; }
  public void applyTo(Level level) {
    Entity entity = level.getEntity(entityID);
    if (entity != null) {
      entity.setDeltaMovement(x, y, z);
      entity.setYRot(yRot);
      entity.setXRot(xRot);
    }
  }
  public static void register(RegisterPayloadHandlersEvent event) {
    event.registrar("1").playToClient(TYPE, CODEC, (packet, context) -> packet.applyTo(context.player().level()));
  }
}
