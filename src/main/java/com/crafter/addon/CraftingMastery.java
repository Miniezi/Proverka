package com.crafter.addon;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/** Tags only newly crafted equipment; existing stacks are never modified. */
@Mod(CraftingMastery.MOD_ID)
public final class CraftingMastery {
    public static final String MOD_ID = "crafting_mastery";
    public static final String TAG = "crafting_mastery";
    public static final String BONUS = "bonus_level";

    public CraftingMastery() {}

    @SubscribeEvent
    public static void onCraft(PlayerEvent.ItemCraftedEvent event) {
        Player player = event.getEntity();
        ItemStack result = event.getCrafting();
        if (result.isEmpty() || !isEquipment(result)) return;
        int levelSnapshot = player.experienceLevel;
        CustomData.update(DataComponents.CUSTOM_DATA, result, tag -> {
            CompoundTag root = tag.getCompound(TAG);
            root.putInt(BONUS, levelSnapshot);
            root.putString("source", player.getUUID().toString());
            tag.put(TAG, root);
        });
    }

    private static boolean isEquipment(ItemStack stack) {
        return stack.isDamageableItem() || stack.has(DataComponents.ATTRIBUTE_MODIFIERS);
    }
}

