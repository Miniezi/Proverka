package slimeknights.tconstruct.common.registration;

import net.minecraft.core.Holder;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionBrewing;
import slimeknights.mantle.registration.deferred.PotionDeferredRegister.PotionType;
import slimeknights.mantle.registration.object.EnumObject;

/** Registers vanilla-compatible mixes on each brewing builder, on either logical side. */
public final class TinkerBrewing {
  private TinkerBrewing() {}

  public static void register(PotionBrewing.Builder builder, EnumObject<PotionType, Potion> variants,
                              Holder<Potion> base, Item ingredient) {
    Holder<Potion> normal = java.util.Objects.requireNonNull(variants.getHolder(PotionType.NORMAL), "Missing normal potion");
    builder.addMix(base, ingredient, normal);
    Holder<Potion> longer = variants.getHolder(PotionType.LONG);
    if (longer != null) builder.addMix(normal, Items.REDSTONE, longer);
    Holder<Potion> strong = variants.getHolder(PotionType.STRONG);
    if (strong != null) builder.addMix(normal, Items.GLOWSTONE_DUST, strong);
  }
}
