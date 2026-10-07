package com.crafter.addon.mixin;

import com.crafter.addon.CraftingMastery;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ResultSlot;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin(ResultSlot.class)
public abstract class TakeResultMixin {
    @Shadow @Final private Player player;
    @Inject(method = "remove", at = @At("HEAD"))
    private void mastery$take(int amount, CallbackInfoReturnable<ItemStack> ci) {
        if (amount > 0) CraftingMastery.finish(player, ((Slot)(Object)this).getItem());
    }
}
