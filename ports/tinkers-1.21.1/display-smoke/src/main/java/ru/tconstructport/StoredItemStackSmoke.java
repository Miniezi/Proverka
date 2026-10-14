package ru.tconstructport;

import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.enchantment.Enchantments;
import slimeknights.tconstruct.library.tools.nbt.StoredItemStack;

final class StoredItemStackSmoke {
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var registries = event.getServer().registryAccess();
    var stack = new ItemStack(Items.ARROW, 3);
    stack.set(DataComponents.CUSTOM_NAME, Component.literal("Stored ammunition"));
    var custom = new CompoundTag(); custom.putString("addon:payload","preserved");
    stack.set(DataComponents.CUSTOM_DATA,CustomData.of(custom));
    stack.enchant(registries.lookupOrThrow(Registries.ENCHANTMENT).getOrThrow(Enchantments.UNBREAKING),2);
    var encoded = StoredItemStack.write(stack,registries);
    var decoded = StoredItemStack.read(encoded,registries);
    if (decoded.getCount()!=3 || !ItemStack.isSameItemSameComponents(stack,decoded)) fail("component roundtrip");
    stack.set(DataComponents.CUSTOM_NAME,Component.literal("changed"));
    if (!StoredItemStack.read(encoded,registries).getHoverName().getString().equals("Stored ammunition")) fail("source alias");
    decoded.set(DataComponents.CUSTOM_NAME,Component.literal("decoded changed"));
    if (!StoredItemStack.read(encoded,registries).getHoverName().getString().equals("Stored ammunition")) fail("decoded alias");
    if (!StoredItemStack.write(ItemStack.EMPTY,registries).isEmpty() || !StoredItemStack.read(new CompoundTag(),registries).isEmpty()) fail("empty sentinel");
    var invalid = new CompoundTag(); invalid.putString("id","tconstruct:missing_item_fixture"); invalid.putInt("count",1);
    if (!StoredItemStack.read(invalid,registries).isEmpty()) fail("invalid item fallback");
    System.out.println("TCONSTRUCT_STORED_ITEMS_OK components=1 enchantments=1 isolation=1 invalid=1");
  }
  private static void fail(String message) {throw new IllegalStateException(message);}
}
