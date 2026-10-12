package slimeknights.tconstruct.common.network;
import net.minecraft.core.BlockPos;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.items.IItemHandlerModifiable;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/** Updates a client block inventory using registry-aware item components. */
public record InventorySlotSyncPacket(ItemStack itemStack, int slot, BlockPos pos) implements TinkerPacket {
  public static final Type<InventorySlotSyncPacket> TYPE = new Type<>(ResourceLocation.fromNamespaceAndPath("tconstruct", "inventory_slot_sync_packet"));
  public static final StreamCodec<RegistryFriendlyByteBuf, InventorySlotSyncPacket> CODEC = StreamCodec.of((buf,packet)->packet.encode(buf),InventorySlotSyncPacket::new);
  public InventorySlotSyncPacket { itemStack=itemStack.copy(); pos=pos.immutable(); }
  public InventorySlotSyncPacket(RegistryFriendlyByteBuf buf) { this(ItemStack.OPTIONAL_STREAM_CODEC.decode(buf),buf.readShort(),buf.readBlockPos()); }
  @Override public Type<InventorySlotSyncPacket> type() { return TYPE; }
  @Override public void encode(RegistryFriendlyByteBuf buf) { ItemStack.OPTIONAL_STREAM_CODEC.encode(buf,itemStack);buf.writeShort(slot);buf.writeBlockPos(pos); }
  @Override public void handle(IPayloadContext context) {
    var level=context.player().level();
    if (!level.hasChunkAt(pos)) return;
    var handler=level.getCapability(Capabilities.ItemHandler.BLOCK,pos,null);
    if (handler instanceof IItemHandlerModifiable inventory && slot>=0 && slot<inventory.getSlots()) {
      inventory.setStackInSlot(slot,itemStack.copy());
      var state=level.getBlockState(pos);
      level.sendBlockUpdated(pos,state,state,net.minecraft.world.level.block.Block.UPDATE_CLIENTS);
    }
  }
}
