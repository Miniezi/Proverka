package slimeknights.tconstruct.common.network;
import net.minecraft.network.RegistryFriendlyByteBuf;
import slimeknights.mantle.network.ISimplePacket;
/** Registry-aware wire format shared by migrated TConstruct payloads. */
public interface TinkerPacket extends ISimplePacket {
  void encode(RegistryFriendlyByteBuf buffer);
}
