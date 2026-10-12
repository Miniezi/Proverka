package slimeknights.tconstruct.common.network;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import slimeknights.tconstruct.library.tools.capability.PersistentDataAttachment;

/** Server-to-client snapshot of the receiving player's persistent modifier data. */
public record SyncPersistentDataPacket(CompoundTag data) implements CustomPacketPayload {
  public static final Type<SyncPersistentDataPacket> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("tconstruct", "persistent_data"));
  public static final StreamCodec<FriendlyByteBuf, SyncPersistentDataPacket> CODEC = StreamCodec.of(
    (buffer, packet) -> buffer.writeNbt(packet.data),
    buffer -> {
      CompoundTag tag = buffer.readNbt();
      if (tag == null) throw new IllegalArgumentException("Missing persistent modifier data");
      return new SyncPersistentDataPacket(tag);
    });

  public SyncPersistentDataPacket { data = data.copy(); }
  @Override public CompoundTag data() { return data.copy(); }
  @Override public Type<SyncPersistentDataPacket> type() { return TYPE; }

  /** Replace in place, preserving existing ModDataNBT views of the attachment. */
  public void applyTo(CompoundTag target) {
    target.getAllKeys().clear();
    target.merge(data.copy());
  }

  public static void register(RegisterPayloadHandlersEvent event) {
    event.registrar("1").playToClient(TYPE, CODEC, (packet, context) ->
      packet.applyTo(context.player().getData(PersistentDataAttachment.TYPE)));
  }
}
