package com.crafter.addon;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;

/**
 * Applies a snapshot only to the newly crafted stack. Existing items never
 * receive a retroactive modifier. Modded equipment is supported when it
 * exposes standard ItemAttributeModifiers.
 */
@Mod(CraftingMastery.MOD_ID)
public final class CraftingMastery {
    public static final String MOD_ID = "crafting_mastery";
    public static final String TAG = "crafting_mastery";
    public static final String BONUS = "bonus_level";
    private static final ResourceLocation ATTACK_ID =
            ResourceLocation.fromNamespaceAndPath(MOD_ID, "crafted_attack");
    private static final ResourceLocation ARMOR_ID =
            ResourceLocation.fromNamespaceAndPath(MOD_ID, "crafted_armor");

    public CraftingMastery() {}

    @SubscribeEvent
    public static void onCraft(PlayerEvent.ItemCraftedEvent event) {
        Player player = event.getEntity();
        ItemStack stack = event.getCrafting();
        if (stack.isEmpty()) return;

        int level = Math.max(0, Math.min(15, player.experienceLevel / 10));
        ItemAttributeModifiers existing =
                stack.getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
        boolean hasAttack = false;
        boolean hasArmor = false;
        ItemAttributeModifiers.Builder builder = ItemAttributeModifiers.builder();
        for (ItemAttributeModifiers.Entry entry : existing.modifiers()) {
            builder.add(entry.attribute(), entry.modifier(), entry.slot());
            hasAttack |= entry.attribute().equals(Attributes.ATTACK_DAMAGE);
            hasArmor |= entry.attribute().equals(Attributes.ARMOR);
        }

        // Every 10 player levels gives one crafting tier, capped at 15.
        // Attack and armor values are additive to the item's own modifiers.
        if (level > 0 && hasAttack) {
            builder.add(Attributes.ATTACK_DAMAGE,
                    new AttributeModifier(ATTACK_ID, level * 0.05D, Operation.ADD_MULTIPLIED_BASE),
                    net.minecraft.world.entity.EquipmentSlotGroup.MAINHAND);
        }
        if (level > 0 && hasArmor) {
            builder.add(Attributes.ARMOR,
                    new AttributeModifier(ARMOR_ID, level * 0.5D, Operation.ADD_VALUE),
                    net.minecraft.world.entity.EquipmentSlotGroup.ARMOR);
        }
        stack.set(DataComponents.ATTRIBUTE_MODIFIERS, builder.build());

        final int snapshot = level;
        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> {
            CompoundTag root = tag.getCompound(TAG);
            root.putInt(BONUS, snapshot);
            root.putString("source", player.getUUID().toString());
            tag.put(TAG, root);
        });
    }
}
