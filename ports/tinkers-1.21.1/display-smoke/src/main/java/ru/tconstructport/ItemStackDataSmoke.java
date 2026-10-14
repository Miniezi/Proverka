package ru.tconstructport;

import io.netty.buffer.Unpooled;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import slimeknights.tconstruct.library.tools.nbt.ItemStackData;

final class ItemStackDataSmoke {
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var stack = new ItemStack(Items.IRON_PICKAXE);
    stack.set(DataComponents.CUSTOM_NAME, Component.literal("Preserved name"));
    stack.set(DataComponents.DAMAGE, 17);
    ItemStackData.read(stack).putString("uncommitted", "discard");
    if (stack.has(DataComponents.CUSTOM_DATA)) fail("read created component");
    var nested = new CompoundTag(); nested.putInt("counter", 2);
    ItemStackData.update(stack, data -> {
      data.put("other_mod", nested);
      data.putString("Material", "tconstruct:iron");
    });
    nested.putInt("counter", 99);
    var copy = stack.copy();
    var before = stack.get(DataComponents.CUSTOM_DATA);
    ItemStackData.update(stack, data -> data.putString("Material", "tconstruct:cobalt"));
    ItemStackData.read(stack).getCompound("other_mod").putInt("counter", 55);
    if (!ItemStackData.read(copy).getString("Material").equals("tconstruct:iron")
        || !before.copyTag().getString("Material").equals("tconstruct:iron")
        || ItemStackData.read(stack).getCompound("other_mod").getInt("counter") != 2
        || stack.getDamageValue() != 17 || !stack.getHoverName().getString().equals("Preserved name")) fail("component isolation or preservation");
    try {
      ItemStackData.update(stack, data -> {data.remove("Material"); throw new IllegalArgumentException("abort");});
      fail("missing edit exception");
    } catch (IllegalArgumentException expected) {}
    if (!ItemStackData.read(stack).getString("Material").equals("tconstruct:cobalt")) fail("failed edit committed");
    var ops = event.getServer().registryAccess().createSerializationContext(NbtOps.INSTANCE);
    var saved = ItemStack.CODEC.encodeStart(ops,stack).getOrThrow();
    var loaded = ItemStack.CODEC.parse(ops,saved).getOrThrow();
    if (!ItemStack.isSameItemSameComponents(stack,loaded)) fail("item persistence");
    var wire = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      ItemStack.STREAM_CODEC.encode(wire,stack);
      if (!ItemStack.isSameItemSameComponents(stack,ItemStack.STREAM_CODEC.decode(wire)) || wire.isReadable()) fail("item wire");
    } finally {wire.release();}
    ItemStackData.update(copy, data -> data.getAllKeys().stream().toList().forEach(data::remove));
    if (copy.has(DataComponents.CUSTOM_DATA) || !stack.has(DataComponents.CUSTOM_DATA)) fail("empty removal");
    ItemStackData.update(ItemStack.EMPTY, data -> data.putInt("invalid",1));
    if (ItemStack.EMPTY.has(DataComponents.CUSTOM_DATA)) fail("empty singleton mutation");
    var working = new CompoundTag();
    var snapshots = new java.util.ArrayList<CompoundTag>();
    var storage = new slimeknights.tconstruct.library.tools.nbt.ModifierDataStorage(working, snapshots::add);
    storage.edit(data -> data.putString("modifier", "first"));
    if (snapshots.size()!=1 || !working.getString("modifier").equals("first")) fail("modifier publication");
    storage.replace(working);
    if (!working.getString("modifier").equals("first")) fail("modifier self-copy");
    snapshots.get(0).putString("modifier", "external");
    if (!working.getString("modifier").equals("first")) fail("published snapshot aliases working data");
    int count = snapshots.size();
    try {
      storage.edit(data -> { data.remove("modifier"); throw new IllegalArgumentException("abort"); });
      fail("missing transaction exception");
    } catch (IllegalArgumentException expected) {}
    if (snapshots.size()!=count || !working.getString("modifier").equals("first")) fail("failed modifier edit committed");
    var replacement = new CompoundTag();
    var child = new CompoundTag(); child.putInt("charge",3); replacement.put("nested",child);
    storage.replace(replacement);
    child.putInt("charge",99);
    if (working.contains("modifier") || working.getCompound("nested").getInt("charge")!=3) fail("replacement isolation");
    storage.edit(data -> data.getCompound("nested").putInt("charge",4));
    if (snapshots.get(snapshots.size()-1).getCompound("nested").getInt("charge")!=4) fail("nested publication");
    System.out.println("TCONSTRUCT_MODIFIER_DATA_OK snapshots=1 self_copy=1 nested=1 atomic=1");
    System.out.println("TCONSTRUCT_ITEM_DATA_OK isolation=1 atomic=1 preservation=1 persistence=1 wire=1");
  }
  private static void fail(String message) {throw new IllegalStateException(message);}
}
