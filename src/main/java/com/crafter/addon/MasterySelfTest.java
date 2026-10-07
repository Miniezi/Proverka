package com.crafter.addon;

import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.level.ClientInformation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.neoforge.common.util.FakePlayerFactory;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.puffish.skillsmod.api.SkillsAPI;

/** Runs only in the isolated CI world when explicitly enabled with a JVM property. */
public final class MasterySelfTest {
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }
    private static double damage(ItemStack stack) {
        return stack.getAttributeModifiers().modifiers().stream()
            .filter(e -> e.attribute().equals(Attributes.ATTACK_DAMAGE))
            .mapToDouble(e -> e.modifier().amount()).sum();
    }
    public static void run(ServerStartedEvent event) {
        var server = event.getServer();
        try {
            var level = server.overworld();
            var profile = new GameProfile(UUID.fromString("92a2f4ca-0cb1-4ad2-bd51-d558371ec901"), "MasteryTest");
            // Skills deliberately suppresses XP for FakePlayer. Use a real player
            // entity with NeoForge's no-network connection in this isolated test.
            var player = new ServerPlayer(server, level, profile, ClientInformation.createDefault());
            player.connection = FakePlayerFactory.get(level, profile).connection;
            var category = SkillsAPI.getCategory(CraftingMastery.CATEGORY).orElseThrow(
                () -> new AssertionError("Bundled tree did not load"));
            check(category.streamSkills().count() == 31, "Expected 31 nodes");
            category.erase(player);
            category.unlock(player);
            var oldSword = new ItemStack(Items.IRON_SWORD);
            var oldCopy = oldSword.copy();
            player.experienceLevel = 100;
            check(!CraftingMastery.improve(player, oldSword), "Vanilla XP must not grant bonuses");
            category.setExtraPoints(player, 50);
            category.getSkill("root").orElseThrow().unlock(player);
            for (String branch : new String[]{"weapon", "tool", "armor"}) {
                for (int i = 1; i <= 10; i++) category.getSkill(branch + "_" + i).orElseThrow().unlock(player);
                check(CraftingMastery.rank(player, branch) == 10, "Skill unlock failed: " + branch);
            }
            check(ItemStack.isSameItemSameComponents(oldSword, oldCopy), "Old item changed");
            var sword = new ItemStack(Items.IRON_SWORD);
            check(CraftingMastery.improve(player, sword), "Sword not improved");
            check(Math.abs(damage(sword) - damage(oldSword) * 1.3) < 0.00001, "Wrong weapon bonus");
            var saved = sword.copy();
            check(!CraftingMastery.improve(player, sword), "Applied twice");
            check(ItemStack.isSameItemSameComponents(saved, sword), "Duplicate application changed item");
            var pickaxe = new ItemStack(Items.IRON_PICKAXE);
            float speed = pickaxe.getDestroySpeed(Blocks.STONE.defaultBlockState());
            CraftingMastery.improve(player, pickaxe);
            check(Math.abs(pickaxe.getDestroySpeed(Blocks.STONE.defaultBlockState()) - speed * 1.5) < 0.001,
                "Wrong mining speed");
            var armor = new ItemStack(Items.IRON_CHESTPLATE);
            var originalArmor = armor.getAttributeModifiers();
            CraftingMastery.improve(player, armor);
            check(armor.has(DataComponents.CUSTOM_DATA), "Armor missing snapshot");
            for (int i = 0; i < originalArmor.modifiers().size(); i++) {
                var before = originalArmor.modifiers().get(i);
                var after = armor.getAttributeModifiers().modifiers().get(i);
                check(before.slot().equals(after.slot()) && before.modifier().id().equals(after.modifier().id()),
                    "Armor slot or identity changed");
                if (before.attribute().equals(Attributes.ARMOR)) check(Math.abs(after.modifier().amount()
                    - before.modifier().amount() * 1.3) < 0.00001, "Wrong armor bonus");
            }
            var bread = new ItemStack(Items.BREAD);
            check(!CraftingMastery.improve(player, bread) && !bread.has(DataComponents.CUSTOM_DATA), "Food changed");
            var menu = new CraftingMenu(1, player.getInventory(), ContainerLevelAccess.create(level, player.blockPosition()));
            var experience = category.getExperience().orElseThrow();
            int xpBefore = experience.getTotal(player);
            player.containerMenu = menu;
            menu.getSlot(1).set(new ItemStack(Items.IRON_INGOT, 2));
            menu.getSlot(4).set(new ItemStack(Items.IRON_INGOT, 2));
            menu.getSlot(7).set(new ItemStack(Items.STICK, 2));
            check(menu.getSlot(0).getItem().is(Items.IRON_SWORD), "Recipe output missing");
            check(menu.getSlot(0).getItem().has(DataComponents.CUSTOM_DATA), "Mixin output hook failed");
            menu.clicked(0, 0, ClickType.QUICK_MOVE, player);
            int swords = 0;
            for (var item : player.getInventory().items) if (item.is(Items.IRON_SWORD)) {
                swords += item.getCount();
                check(Math.abs(damage(item) - damage(oldSword) * 1.3) < 0.00001, "Shift craft lost bonus");
            }
            check(swords == 2, "Shift craft did not produce two swords");
            check(experience.getTotal(player) > xpBefore, "Crafting did not grant skill XP");
            menu.getSlot(1).set(new ItemStack(Items.IRON_INGOT));
            menu.getSlot(4).set(new ItemStack(Items.IRON_INGOT));
            menu.getSlot(7).set(new ItemStack(Items.STICK));
            menu.clicked(0, 0, ClickType.PICKUP, player);
            check(menu.getCarried().is(Items.IRON_SWORD) && menu.getCarried().has(DataComponents.CUSTOM_DATA),
                "Normal craft lost bonus");
            var inventoryMenu = player.inventoryMenu;
            player.containerMenu = inventoryMenu;
            inventoryMenu.getSlot(2).set(new ItemStack(Items.IRON_INGOT));
            inventoryMenu.getSlot(3).set(new ItemStack(Items.IRON_INGOT));
            check(inventoryMenu.getSlot(0).getItem().is(Items.SHEARS), "2x2 recipe output missing");
            inventoryMenu.clicked(0, 0, ClickType.PICKUP, player);
            check(inventoryMenu.getCarried().has(DataComponents.CUSTOM_DATA), "2x2 craft lost bonus");
            category.resetSkills(player);
            check(CraftingMastery.rank(player, "weapon") == 0, "Reset failed");
            check(ItemStack.isSameItemSameComponents(saved, sword), "Reset changed crafted item");
            var restored = ItemStack.parseOptional(server.registryAccess(), (net.minecraft.nbt.CompoundTag) sword.save(server.registryAccess()));
            check(ItemStack.isSameItemSameComponents(saved, restored), "Bonus lost on serialization");
            var fresh = new ItemStack(Items.IRON_SWORD);
            check(!CraftingMastery.improve(player, fresh), "Reset still buffs new items");
            System.out.println("CRAFTING_MASTERY_SELFTEST_PASSED");
        } catch (Throwable error) {
            error.printStackTrace();
            System.out.println("CRAFTING_MASTERY_SELFTEST_FAILED");
        } finally {
            server.halt(false);
        }
    }
}
