package ru.tconstructport;

import com.google.gson.JsonParser;
import com.mojang.serialization.JsonOps;
import io.netty.buffer.Unpooled;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.RegisterEvent;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import slimeknights.tconstruct.library.recipe.ingredient.NoContainerIngredient;
import slimeknights.tconstruct.library.recipe.ingredient.MaterialValueRange;
import slimeknights.tconstruct.library.recipe.ingredient.BlockTagIngredient;
import slimeknights.tconstruct.library.recipe.ingredient.InstrumentIngredient;

final class CustomIngredientSmoke {
  static void init(IEventBus bus) { bus.addListener(CustomIngredientSmoke::register); }
  private static void register(RegisterEvent event) {
    event.register(NeoForgeRegistries.Keys.INGREDIENT_TYPES, helper -> {
      helper.register(NoContainerIngredient.ID,NoContainerIngredient.TYPE);
      helper.register(BlockTagIngredient.ID,BlockTagIngredient.TYPE);
      helper.register(InstrumentIngredient.ID,InstrumentIngredient.TYPE);
    });
  }
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var ops = event.getServer().registryAccess().createSerializationContext(JsonOps.INSTANCE);
    var ingredient = NoContainerIngredient.of(Items.STICK,Items.MILK_BUCKET);
    if (!ingredient.test(new ItemStack(Items.STICK)) || ingredient.test(new ItemStack(Items.MILK_BUCKET)) || ingredient.isSimple()) fail("craft remainder predicate");
    if (!(ingredient.getCustomIngredient() instanceof NoContainerIngredient)) fail("native wrapper");
    var json = Ingredient.CODEC.encodeStart(ops,ingredient).getOrThrow();
    var restored = Ingredient.CODEC.parse(ops,json).getOrThrow();
    if (!restored.test(new ItemStack(Items.STICK)) || restored.test(new ItemStack(Items.MILK_BUCKET))) fail("registered codec");
    var legacy = Ingredient.CODEC.parse(ops,JsonParser.parseString("{\"type\":\"tconstruct:no_container\",\"item\":\"minecraft:stick\"}")).getOrThrow();
    if (!legacy.test(new ItemStack(Items.STICK))) fail("legacy inline ingredient");
    var bad = Ingredient.CODEC.parse(ops,JsonParser.parseString("{\"type\":\"tconstruct:no_container\"}"));
    if (bad.isSuccess()) fail("missing nested ingredient");
    if (Ingredient.CODEC.parse(ops,JsonParser.parseString("{\"type\":\"tconstruct:no_container\",\"item\":\"minecraft:air\"}")).isSuccess()) fail("air ingredient accepted");
    var tagged = Ingredient.CODEC.parse(ops,JsonParser.parseString("{\"type\":\"tconstruct:no_container\",\"tag\":\"minecraft:planks\"}")).getOrThrow();
    if (!tagged.test(new ItemStack(Items.OAK_PLANKS)) || tagged.test(new ItemStack(Items.STICK))) fail("legacy inline tag");
    var named = new ItemStack(Items.STICK);
    named.set(DataComponents.CUSTOM_NAME,Component.literal("material test"));
    var component = net.neoforged.neoforge.common.crafting.DataComponentIngredient.of(false,DataComponents.CUSTOM_NAME,Component.literal("material test"),Items.STICK);
    var nested = NoContainerIngredient.of(component);
    var buf = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      Ingredient.CONTENTS_STREAM_CODEC.encode(buf,ingredient);
      Ingredient.CONTENTS_STREAM_CODEC.encode(buf,nested);
      var decoded = Ingredient.CONTENTS_STREAM_CODEC.decode(buf);
      var componentCopy = Ingredient.CONTENTS_STREAM_CODEC.decode(buf);
      if (!decoded.test(new ItemStack(Items.STICK)) || decoded.test(new ItemStack(Items.MILK_BUCKET))
          || !componentCopy.test(named) || componentCopy.test(new ItemStack(Items.STICK)) || buf.isReadable()) fail("custom ingredient wire");
    } finally {buf.release();}
    var blocks = new BlockTagIngredient(net.minecraft.tags.BlockTags.DIRT).toVanilla();
    if (!blocks.test(new ItemStack(Items.DIRT)) || blocks.test(new ItemStack(Items.DIAMOND)) || blocks.test(ItemStack.EMPTY)) fail("block tag matching");
    var blockJson = Ingredient.CODEC.encodeStart(ops,blocks).getOrThrow();
    if (!Ingredient.CODEC.parse(ops,blockJson).getOrThrow().test(new ItemStack(Items.DIRT))) fail("block tag JSON");
    var blockBuf = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      Ingredient.CONTENTS_STREAM_CODEC.encode(blockBuf,blocks);
      if (!Ingredient.CONTENTS_STREAM_CODEC.decode(blockBuf).test(new ItemStack(Items.DIRT)) || blockBuf.isReadable()) fail("block tag wire");
    } finally {blockBuf.release();}
    if (new BlockTagIngredient(net.minecraft.tags.BlockTags.FIRE).getItems().findAny().isPresent()) fail("air item forms");
    var horn = new ItemStack(Items.GOAT_HORN);
    var ponder = net.minecraft.world.item.Instruments.PONDER_GOAT_HORN;
    horn.set(DataComponents.INSTRUMENT,net.minecraft.core.registries.BuiltInRegistries.INSTRUMENT.getHolderOrThrow(ponder));
    var instrument = InstrumentIngredient.of(Items.GOAT_HORN,ponder);
    var absent = horn.copy(); absent.remove(DataComponents.INSTRUMENT);
    var wrong = horn.copy(); wrong.set(DataComponents.INSTRUMENT,net.minecraft.core.registries.BuiltInRegistries.INSTRUMENT.getHolderOrThrow(net.minecraft.world.item.Instruments.SING_GOAT_HORN));
    var excluded = InstrumentIngredient.of(Items.GOAT_HORN,net.minecraft.tags.InstrumentTags.GOAT_HORNS);
    if (!instrument.test(horn) || instrument.test(absent) || instrument.test(wrong)
        || instrument.test(new ItemStack(Items.STICK)) || instrument.isSimple()
        || excluded.test(horn) || !excluded.test(absent)) fail("instrument component predicate");
    for (var value : java.util.List.of(instrument,excluded)) {
      var copy = Ingredient.CODEC.parse(ops,Ingredient.CODEC.encodeStart(ops,value).getOrThrow()).getOrThrow();
      if (copy.test(horn)!=value.test(horn) || copy.test(absent)!=value.test(absent)) fail("instrument JSON");
      if (java.util.Arrays.stream(value.getItems()).anyMatch(stack -> !value.test(stack))) fail("instrument display");
      var wire = new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
      try {
        Ingredient.CONTENTS_STREAM_CODEC.encode(wire,value);
        var decoded = Ingredient.CONTENTS_STREAM_CODEC.decode(wire);
        if (decoded.test(horn)!=value.test(horn) || decoded.test(absent)!=value.test(absent) || wire.isReadable()) fail("instrument wire");
      } finally {wire.release();}
    }
    for (String fields : new String[]{"",",\"instrument\":\"minecraft:ponder_goat_horn\",\"ignore\":\"minecraft:goat_horns\""}) {
      if (Ingredient.CODEC.parse(ops,JsonParser.parseString("{\"type\":\"tconstruct:instrument\",\"item\":\"minecraft:goat_horn\""+fields+"}")).isSuccess()) fail("invalid instrument selector");
    }
    var exact = MaterialValueRange.CODEC.parse(JsonOps.INSTANCE,JsonParser.parseString("2")).getOrThrow();
    var range = MaterialValueRange.CODEC.parse(JsonOps.INSTANCE,JsonParser.parseString("{\"min\":1,\"max\":3}")).getOrThrow();
    var unbounded = MaterialValueRange.CODEC.parse(JsonOps.INSTANCE,JsonParser.parseString("{} ")).getOrThrow();
    if (!exact.test(2) || exact.test(1) || !range.test(1) || !range.test(3) || range.test(4)
        || !unbounded.test(1000) || unbounded.test(Float.POSITIVE_INFINITY) || unbounded.test(Float.NaN)) fail("quantity bounds");
    for (String invalid : new String[]{"-1","{\"min\":3,\"max\":1}","{\"min\":-1}"}) {
      if (MaterialValueRange.CODEC.parse(JsonOps.INSTANCE,JsonParser.parseString(invalid)).isSuccess()) fail("invalid quantity range");
    }
    var rangeCodec = net.minecraft.network.codec.ByteBufCodecs.fromCodec(MaterialValueRange.CODEC);
    for (var value : java.util.List.of(exact,range,unbounded,new MaterialValueRange(1f/9f,1f/9f))) {
      var encoded = MaterialValueRange.CODEC.encodeStart(JsonOps.INSTANCE,value).getOrThrow();
      if (!MaterialValueRange.CODEC.parse(JsonOps.INSTANCE,encoded).getOrThrow().equals(value)) fail("quantity codec roundtrip");
      var bytes = Unpooled.buffer();
      try {
        rangeCodec.encode(bytes,value);
        if (!rangeCodec.decode(bytes).equals(value) || bytes.isReadable()) fail("quantity wire roundtrip");
      } finally {bytes.release();}
    }
    System.out.println("TCONSTRUCT_CUSTOM_INGREDIENTS_OK registration=1 containers=1 nested_components=1 json=1 wire=1 ranges=1");
  }
  private static void fail(String message) { throw new IllegalStateException(message); }
}
