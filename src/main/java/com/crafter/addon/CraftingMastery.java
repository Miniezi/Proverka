package com.crafter.addon;

import java.util.ArrayList;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import net.minecraft.world.item.component.Tool;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.Skill;

@Mod(CraftingMastery.MOD_ID)
public final class CraftingMastery {
    public static final String MOD_ID = "crafting_mastery";
    public static final ResourceLocation CATEGORY = ResourceLocation.fromNamespaceAndPath("crafter", "crafting");

    public CraftingMastery() {
        NeoForge.EVENT_BUS.addListener(CraftingMastery::onCraft);
        if (Boolean.getBoolean("crafting_mastery.selftest")) NeoForge.EVENT_BUS.addListener(MasterySelfTest::run);
    }

    public static int rank(ServerPlayer player, String branch) {
        return SkillsAPI.getCategory(CATEGORY).map(category -> {
            int count = 0;
            for (int i = 1; i <= 10; i++) {
                if (category.getSkill(branch + "_" + i)
                    .map(skill -> skill.getState(player) == Skill.State.UNLOCKED).orElse(false)) count++;
            }
            return count;
        }).orElse(0);
    }

    private static void onCraft(PlayerEvent.ItemCraftedEvent event) {
        // Fallback for modded tables publishing the standard crafting event.
        improve(event.getEntity(), event.getCrafting());
    }

    /** Mutates only freshly assembled outputs, never the player's inventory. */
    public static boolean improve(Player player, ItemStack stack) {
        if (!(player instanceof ServerPlayer serverPlayer) || stack.isEmpty()) return false;
        if (stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).contains(MOD_ID)) return false;
        int weapon = rank(serverPlayer, "weapon");
        int toolRank = rank(serverPlayer, "tool");
        int armor = rank(serverPlayer, "armor");
        // Snapshot base item modifiers only. Event-derived modifiers must not be
        // baked in, otherwise other mods could apply their bonuses twice.
        ItemAttributeModifiers attributes = stack.getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
        if (attributes.modifiers().isEmpty()) attributes = stack.getItem().getDefaultAttributeModifiers(stack);
        var builder = ItemAttributeModifiers.builder();
        boolean changedAttributes = false;
        for (var entry : attributes.modifiers()) {
            AttributeModifier modifier = entry.modifier();
            double factor = 1.0;
            if (modifier.operation() == AttributeModifier.Operation.ADD_VALUE && modifier.amount() > 0) {
                if (entry.attribute().equals(Attributes.ATTACK_DAMAGE)) factor += weapon * 0.03;
                if (entry.attribute().equals(Attributes.ARMOR)) factor += armor * 0.03;
            }
            if (factor != 1.0) {
                modifier = new AttributeModifier(modifier.id(), modifier.amount() * factor, modifier.operation());
                changedAttributes = true;
            }
            builder.add(entry.attribute(), modifier, entry.slot());
        }
        Tool tool = stack.get(DataComponents.TOOL);
        boolean changedTool = tool != null && toolRank > 0;
        if (!changedAttributes && !changedTool) return false;
        if (changedAttributes) stack.set(DataComponents.ATTRIBUTE_MODIFIERS,
            builder.build().withTooltip(attributes.showInTooltip()));
        if (changedTool) {
            float factor = 1.0F + toolRank * 0.05F;
            var rules = new ArrayList<Tool.Rule>();
            for (var rule : tool.rules()) rules.add(new Tool.Rule(rule.blocks(),
                rule.speed().map(speed -> speed * factor), rule.correctForDrops()));
            stack.set(DataComponents.TOOL, new Tool(rules, tool.defaultMiningSpeed() * factor, tool.damagePerBlock()));
        }
        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> {
            CompoundTag snapshot = new CompoundTag();
            snapshot.putInt("version", 2);
            snapshot.putInt("weapon", weapon);
            snapshot.putInt("tool", toolRank);
            snapshot.putInt("armor", armor);
            tag.put(MOD_ID, snapshot);
        });
        return true;
    }
}
