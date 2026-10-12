package slimeknights.tconstruct.common.network;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.world.item.enchantment.Enchantment;
public final class TinkerPacketCodecs {
  private TinkerPacketCodecs() {}
  public static final StreamCodec<RegistryFriendlyByteBuf, Enchantment> ENCHANTMENT = ByteBufCodecs.registry(Registries.ENCHANTMENT);
}
