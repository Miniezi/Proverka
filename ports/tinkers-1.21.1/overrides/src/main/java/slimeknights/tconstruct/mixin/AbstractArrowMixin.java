package slimeknights.tconstruct.mixin;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Vanilla 1.21 recognizes only Items.CROSSBOW; include TConstruct's tagged weapons. */
@Mixin(AbstractArrow.class)
public abstract class AbstractArrowMixin {
  @Unique private static final TagKey<Item> TCONSTRUCT_CROSSBOWS = TagKey.create(Registries.ITEM,
    ResourceLocation.fromNamespaceAndPath("tconstruct", "modifiable/ranged/crossbows"));

  @Inject(method = "shotFromCrossbow", at = @At("RETURN"), cancellable = true)
  private void tconstruct$recognizeCrossbows(CallbackInfoReturnable<Boolean> result) {
    if (!result.getReturnValueZ()) {
      ItemStack weapon = ((AbstractArrow)(Object)this).getWeaponItem();
      if (weapon != null && weapon.is(TCONSTRUCT_CROSSBOWS)) result.setReturnValue(true);
    }
  }
}
