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
            for (int i = 1; i <= 20; i++) {
                if (category.getSkill(branch + "_" + i)
                    .map(skill -> skill.getState(player) == Skill.State.UNLOCKED).orElse(false)) count++;
            }
            return count;
        }).orElse(0);
    }

    private static void onCraft(PlayerEvent.ItemCraftedEvent event) {
        // Fallback for modded tables publishing the standard crafting event.
        improve(event.getEntity(), event.getCrafting());
        finish(event.getEntity(), event.getCrafting());
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
                if (entry.attribute().equals(Attributes.ATTACK_DAMAGE)) factor += weapon * 0.015;
                if (entry.attribute().equals(Attributes.ARMOR)) factor += armor * 0.015;
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
            float factor = 1.0F + toolRank * 0.015F;
            var rules = new ArrayList<Tool.Rule>();
            for (var rule : tool.rules()) rules.add(new Tool.Rule(rule.blocks(),
                rule.speed().map(speed -> speed * factor), rule.correctForDrops()));
            stack.set(DataComponents.TOOL, new Tool(rules, tool.defaultMiningSpeed() * factor, tool.damagePerBlock()));
        }
        boolean hasAttack = attributes.modifiers().stream().anyMatch(e -> e.attribute().equals(Attributes.ATTACK_DAMAGE));
        boolean hasArmor = attributes.modifiers().stream().anyMatch(e -> e.attribute().equals(Attributes.ARMOR));
        int durabilityRank = tool != null ? toolRank : Math.max(hasAttack ? weapon : 0, hasArmor ? armor : 0);
        if (stack.isDamageableItem() && durabilityRank > 0) {
            int base = stack.getMaxDamage();
            stack.set(DataComponents.MAX_DAMAGE, Math.max(base + 1, Math.round(base * (1.0F + durabilityRank * 0.015F))));
        }
        CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> {
            CompoundTag snapshot = new CompoundTag();
            snapshot.putInt("version", 3);
            snapshot.putInt("weapon", weapon);
            snapshot.putInt("tool", toolRank);
            snapshot.putInt("armor", armor);
            tag.put(MOD_ID, snapshot);
        });
        return true;
    }

    public static void finish(Player player, ItemStack stack) {
        finish(player, stack, () -> player.getRandom().nextDouble());
    }

    // Chance is rolled when taking the output, never while browsing recipe previews.
    static void finish(Player player, ItemStack stack, java.util.function.DoubleSupplier random) {
        if (!(player instanceof ServerPlayer serverPlayer) || stack.isEmpty()) return;
        improve(player, stack);
        var data = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        var snapshot = data.getCompound(MOD_ID);
        if (snapshot.getInt("version") != 3 || snapshot.getBoolean("rolled")) return;
        boolean weapon = lucky(serverPlayer, "weapon", random);
        boolean tool = lucky(serverPlayer, "tool", random);
        boolean armor = lucky(serverPlayer, "armor", random);
        var attributes = stack.getOrDefault(DataComponents.ATTRIBUTE_MODIFIERS, ItemAttributeModifiers.EMPTY);
        var builder = ItemAttributeModifiers.builder();
        boolean changed = false;
        for (var entry : attributes.modifiers()) {
            var modifier = entry.modifier();
            if (modifier.operation() == AttributeModifier.Operation.ADD_VALUE && modifier.amount() > 0 &&
                ((weapon && entry.attribute().equals(Attributes.ATTACK_DAMAGE)) ||
                 (armor && entry.attribute().equals(Attributes.ARMOR)))) {
                modifier = new AttributeModifier(modifier.id(), modifier.amount() * 1.5, modifier.operation());
                changed = true;
            }
            builder.add(entry.attribute(), modifier, entry.slot());
        }
        if (changed) stack.set(DataComponents.ATTRIBUTE_MODIFIERS, builder.build().withTooltip(attributes.showInTooltip()));
        Tool mining = stack.get(DataComponents.TOOL);
        if (tool && mining != null) {
            var rules = new ArrayList<Tool.Rule>();
            for (var rule : mining.rules()) rules.add(new Tool.Rule(rule.blocks(),
                rule.speed().map(speed -> speed * 1.5F), rule.correctForDrops()));
            stack.set(DataComponents.TOOL, new Tool(rules, mining.defaultMiningSpeed() * 1.5F, mining.damagePerBlock()));
        }
        if (stack.isDamageableItem()) {
            int base = stack.getMaxDamage();
            stack.set(DataComponents.MAX_DAMAGE, Math.max(base + 1, Math.round(base * 1.5F)));
        }
        snapshot.putBoolean("rolled", true);
        snapshot.putBoolean("rare_weapon", weapon);
        snapshot.putBoolean("rare_tool", tool);
        snapshot.putBoolean("rare_armor", armor);
        data.put(MOD_ID, snapshot);
        stack.set(DataComponents.CUSTOM_DATA, CustomData.of(data));
    }

    private static boolean lucky(ServerPlayer player, String branch, java.util.function.DoubleSupplier random) {
        return SkillsAPI.getCategory(CATEGORY).flatMap(c -> c.getSkill(branch + "_master"))
            .map(s -> s.getState(player) == Skill.State.UNLOCKED).orElse(false) && random.getAsDouble() < 0.05;
    }
}
