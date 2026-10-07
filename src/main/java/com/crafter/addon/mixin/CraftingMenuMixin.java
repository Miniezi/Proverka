package com.crafter.addon.mixin;

import com.crafter.addon.CraftingMastery;
import net.minecraft.network.protocol.game.ClientboundContainerSetSlotPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.ResultContainer;
import net.minecraft.world.item.crafting.CraftingRecipe;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(CraftingMenu.class)
public abstract class CraftingMenuMixin {
    // Shared by the 2x2 inventory grid and the 3x3 table; every Shift-click iteration.
    @Inject(method = "slotChangedCraftingGrid", at = @At("TAIL"))
    private static void mastery$output(AbstractContainerMenu menu, Level level, Player player,
            CraftingContainer input, ResultContainer result, RecipeHolder<CraftingRecipe> recipe,
            CallbackInfo ci) {
        var output = result.getItem(0);
        if (CraftingMastery.improve(player, output)) {
            menu.setRemoteSlot(0, output);
            ((ServerPlayer) player).connection.send(new ClientboundContainerSetSlotPacket(
                menu.containerId, menu.incrementStateId(), 0, output));
        }
    }
}
