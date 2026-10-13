package ru.tconstructport;

import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import io.netty.buffer.Unpooled;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.CraftingInput;
import net.minecraft.world.item.crafting.ShapedRecipe;
import slimeknights.tconstruct.library.recipe.material.MaterialRecipePattern;

final class MaterialPatternSmoke {
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var ops = event.getServer().registryAccess().createSerializationContext(JsonOps.INSTANCE);
    String definition = "{\"pattern\":[\" A \",\" B \"],\"key\":{\"A\":{\"item\":\"minecraft:iron_ingot\"},\"B\":{\"item\":\"minecraft:stick\"}},\"parts\":\"ABA\"}";
    var layout = MaterialRecipePattern.CODEC.codec().parse(ops,JsonParser.parseString(definition)).getOrThrow();
    check(layout);
    var recipe = new ShapedRecipe("", CraftingBookCategory.MISC, layout.pattern(), new ItemStack(Items.IRON_SWORD),true);
    var input = CraftingInput.of(1,2,java.util.List.of(new ItemStack(Items.IRON_INGOT),new ItemStack(Items.STICK)));
    if (!recipe.matches(input,event.getServer().overworld()) || recipe.getWidth()!=1 || recipe.getHeight()!=2) fail("trimmed shape");
    if (layout.parts().get(0)!=recipe.getIngredients().get(0) || layout.parts().get(1)!=recipe.getIngredients().get(1)) fail("key identity");
    var buf = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      MaterialRecipePattern.STREAM_CODEC.encode(buf,layout);
      var copy = MaterialRecipePattern.STREAM_CODEC.decode(buf);
      check(copy);
      var roundtripRecipe = new ShapedRecipe("",CraftingBookCategory.MISC,copy.pattern(),new ItemStack(Items.IRON_SWORD),true);
      if (copy.parts().get(0)!=roundtripRecipe.getIngredients().get(0) || !roundtripRecipe.matches(input,event.getServer().overworld()) || buf.isReadable()) fail("wire identity/matching");
      var serialized = MaterialRecipePattern.CODEC.codec().encodeStart(ops,copy).getOrThrow();
      check(MaterialRecipePattern.CODEC.codec().parse(ops,serialized).getOrThrow());
    } finally {buf.release();}
    // Verify custom ingredient components survive JSON and registry-aware wire encoding.
    var componentJson = JsonParser.parseString(definition).getAsJsonObject();
    var named = new ItemStack(Items.IRON_INGOT);
    named.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME,net.minecraft.network.chat.Component.literal("tempered"));
    var custom = net.neoforged.neoforge.common.crafting.DataComponentIngredient.of(false,
      net.minecraft.core.component.DataComponents.CUSTOM_NAME,net.minecraft.network.chat.Component.literal("tempered"),Items.IRON_INGOT);
    componentJson.getAsJsonObject("key").add("A",net.minecraft.world.item.crafting.Ingredient.CODEC.encodeStart(ops,custom).getOrThrow());
    var componentLayout = MaterialRecipePattern.CODEC.codec().parse(ops,componentJson).getOrThrow();
    var componentBuf = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      MaterialRecipePattern.STREAM_CODEC.encode(componentBuf,componentLayout);
      var restored = MaterialRecipePattern.STREAM_CODEC.decode(componentBuf);
      if (!restored.parts().get(0).test(named) || restored.parts().get(0).test(new ItemStack(Items.IRON_INGOT))
          || restored.parts().get(0)!=restored.parts().get(2)) fail("custom component ingredient");
    } finally {componentBuf.release();}
    for (String invalid : new String[]{definition.replace("ABA","C"),definition.replace(" A "," A"),definition.replace(" A "," C ")}) {
      if (MaterialRecipePattern.CODEC.codec().parse(ops,JsonParser.parseString(invalid)).isSuccess()) fail("invalid pattern accepted");
    }
    System.out.println("TCONSTRUCT_MATERIAL_PATTERN_OK identity=1 repeated_parts=1 shape=1 json=1 wire=1 rejection=1");
  }
  private static void check(MaterialRecipePattern pattern) {
    if (pattern.parts().size()!=3 || pattern.parts().get(0)!=pattern.parts().get(2)
        || pattern.parts().get(0)==pattern.parts().get(1)) fail("part ordering/repeated identity");
  }
  private static void fail(String message) {throw new IllegalStateException(message);}
}
