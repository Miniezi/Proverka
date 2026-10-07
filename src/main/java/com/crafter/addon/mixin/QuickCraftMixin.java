package com.crafter.addon.mixin;

import com.crafter.addon.CraftingMastery;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin({CraftingMenu.class, InventoryMenu.class})
public abstract class QuickCraftMixin {
    @Inject(method = "quickMoveStack", at = @At("HEAD"))
    private void mastery$quick(Player player, int index, CallbackInfoReturnable<ItemStack> ci) {
        if (index == 0 && player.getInventory().getFreeSlot() >= 0)
            CraftingMastery.finish(player, ((AbstractContainerMenu)(Object)this).getSlot(0).getItem());
    }
}
