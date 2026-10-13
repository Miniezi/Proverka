package ru.tconstructport;

import com.google.gson.JsonParser;
import io.netty.buffer.Unpooled;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import slimeknights.tconstruct.library.recipe.ingredient.SizedIngredient;
import slimeknights.tconstruct.library.recipe.ingredient.FluidIngredient;

final class IngredientSmoke {
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var context = slimeknights.mantle.data.loadable.field.ContextKey.registryContext(event.getServer().registryAccess());
    var items = SizedIngredient.fromItems(3, Items.IRON_INGOT, Items.GOLD_INGOT);
    if (items.test(new ItemStack(Items.IRON_INGOT,2)) || !items.test(new ItemStack(Items.GOLD_INGOT,3))
        || items.test(new ItemStack(Items.DIAMOND,64))) fail("item quantity/type");
    if (!SizedIngredient.EMPTY.isEmpty() || !SizedIngredient.EMPTY.test(ItemStack.EMPTY)
        || SizedIngredient.EMPTY.test(new ItemStack(Items.IRON_INGOT))) fail("empty ingredient");
    var displayed = items.getMatchingStacks();
    if (displayed.size()!=2 || displayed.stream().anyMatch(s -> s.getCount()!=3)
        || items.getIngredient().getItems()[0].getCount()!=1) fail("display quantity mutates source");
    var json = SizedIngredient.LOADABLE.serialize(items,context);
    var restored = SizedIngredient.LOADABLE.convert(json,"ingredient",context);
    if (restored.getAmountNeeded()!=3 || !restored.test(new ItemStack(Items.GOLD_INGOT,3))) fail("item JSON");
    var legacy = SizedIngredient.LOADABLE.convert(JsonParser.parseString("{\"item\":\"minecraft:iron_ingot\",\"amount_needed\":4}"),"ingredient",context);
    if (legacy.getAmountNeeded()!=4 || !legacy.test(new ItemStack(Items.IRON_INGOT,4))) fail("flat legacy JSON");
    var nested = SizedIngredient.LOADABLE.convert(JsonParser.parseString("{\"ingredient\":{\"item\":\"minecraft:iron_ingot\"},\"amount_needed\":2}"),"ingredient",context);
    if (nested.getAmountNeeded()!=2) fail("nested legacy JSON");
    try { SizedIngredient.LOADABLE.convert(JsonParser.parseString("{\"item\":\"minecraft:iron_ingot\",\"amount_needed\":0}"),"ingredient",context); fail("zero JSON amount"); }
    catch (com.google.gson.JsonSyntaxException expected) {}

    var fluids = FluidIngredient.of(FluidIngredient.of(Fluids.WATER,250),FluidIngredient.of(Fluids.LAVA,750));
    if (!fluids.test(new FluidStack(Fluids.WATER,250)) || fluids.test(new FluidStack(Fluids.WATER,249))
        || !fluids.test(new FluidStack(Fluids.LAVA,750)) || fluids.test(new FluidStack(Fluids.LAVA,749))
        || fluids.getAmount(Fluids.WATER)!=250 || fluids.getAmount(Fluids.LAVA)!=750) fail("fluid alternatives");
    var tag = FluidIngredient.of(FluidTags.WATER,100);
    if (!tag.test(Fluids.WATER) || !tag.test(Fluids.FLOWING_WATER) || tag.test(Fluids.LAVA)) fail("fluid tag");
    var fluidJson = FluidIngredient.LOADABLE.serialize(fluids);
    var fluidCopy = FluidIngredient.LOADABLE.convert(fluidJson,"fluid");
    if (!fluidJson.isJsonArray() || fluidCopy.getAmount(Fluids.LAVA)!=750 || fluidCopy.test(new FluidStack(Fluids.LAVA,749))) fail("fluid JSON");
    var oldName = FluidIngredient.LOADABLE.convert(JsonParser.parseString("{\"name\":\"minecraft:water\",\"amount\":125}"),"fluid");
    if (oldName.getAmount(Fluids.WATER)!=125 || !oldName.test(Fluids.WATER)) fail("legacy fluid name");
    if (!FluidIngredient.EMPTY.test(FluidStack.EMPTY) || FluidIngredient.of(Fluids.WATER,0)!=FluidIngredient.EMPTY) fail("empty fluid");
    var buf = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      SizedIngredient.LOADABLE.encode(buf,items);
      FluidIngredient.LOADABLE.encode(buf,fluids);
      FluidIngredient.LOADABLE.encode(buf,tag);
      FluidIngredient.LOADABLE.encode(buf,FluidIngredient.EMPTY);
      var itemWire = SizedIngredient.LOADABLE.decode(buf);
      var fluidWire = FluidIngredient.LOADABLE.decode(buf);
      var tagWire = FluidIngredient.LOADABLE.decode(buf);
      var emptyWire = FluidIngredient.LOADABLE.decode(buf);
      if (itemWire.getAmountNeeded()!=3 || !itemWire.test(new ItemStack(Items.IRON_INGOT,3))
          || fluidWire.getAmount(Fluids.LAVA)!=750 || !fluidWire.test(new FluidStack(Fluids.WATER,250))
          || !tagWire.test(Fluids.FLOWING_WATER) || !emptyWire.test(FluidStack.EMPTY) || buf.isReadable()) fail("wire roundtrip");
    } finally { buf.release(); }
    System.out.println("TCONSTRUCT_INGREDIENTS_OK quantity=1 alternatives=1 tags=1 json=1 wire=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
