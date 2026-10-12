package slimeknights.tconstruct.common.network;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.neoforged.neoforge.network.handling.IPayloadContext;
/** Clientbound block entity dispatch; never loads a missing chunk. */
public interface TinkerBlockEntityPacket<T> extends TinkerPacket {
  BlockPos pos();
  Class<T> blockEntityType();
  void handleBlockEntity(IPayloadContext context, T blockEntity);
  @Override default void handle(IPayloadContext context) {
    Level level = context.player().level();
    if (!level.hasChunkAt(pos())) return;
    Object entity = level.getBlockEntity(pos());
    if (blockEntityType().isInstance(entity)) handleBlockEntity(context, blockEntityType().cast(entity));
  }
}
