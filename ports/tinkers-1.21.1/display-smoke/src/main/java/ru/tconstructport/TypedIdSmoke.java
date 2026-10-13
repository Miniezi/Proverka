package ru.tconstructport;
import io.netty.buffer.Unpooled;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import slimeknights.tconstruct.library.tools.stat.ToolStatId;
import slimeknights.mantle.util.typed.TypedMap;

final class TypedIdSmoke {
  record Value(int number,String text) {}
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var vanilla=ResourceLocation.fromNamespaceAndPath("tconstruct","damage");
    var typed=new ToolStatId(vanilla);
    if(!vanilla.equals(typed) || !typed.equals(vanilla) || typed.hashCode()!=vanilla.hashCode() || typed.compareTo(vanilla)!=0) fail("identifier equivalence");
    var map=new java.util.HashMap<ResourceLocation,String>();map.put(typed,"value");
    if(!"value".equals(map.get(vanilla))) fail("registry key lookup");
    for(String value:new String[]{"tconstruct:damage","damage",":damage","minecraft:path/to/item"}) {
      var parsed=ToolStatId.tryParse(value);
      if(parsed==null || !parsed.equals(ResourceLocation.parse(value)) || !new ToolStatId(value).equals(parsed)) fail("valid parse");
    }
    for(String value:new String[]{"Bad:damage","minecraft:BAD","bad space", "a:b:c"}) {
      if(ToolStatId.tryParse(value)!=null) fail("invalid ID accepted");
      try {new ToolStatId(value);fail("throwing constructor accepted invalid ID");} catch(net.minecraft.ResourceLocationException expected) {}
    }
    if(ToolStatId.tryBuild("Bad","path")!=null || ToolStatId.tryBuild("tconstruct","path/sub")==null) fail("pair validation");
    var buf=new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      ToolStatId.PARSER.encode(buf,typed);
      if(!ToolStatId.PARSER.decode(buf,TypedMap.EMPTY).equals(typed) || buf.isReadable()) fail("typed ID wire roundtrip");
    } finally {buf.release();}
    var blocks=net.minecraft.core.registries.BuiltInRegistries.BLOCK;
    var items=net.minecraft.core.registries.BuiltInRegistries.ITEM;
    if(blocks.get(ResourceLocation.parse("tconstruct:silky_jewel_block"))!=net.minecraft.world.level.block.Blocks.EMERALD_BLOCK
      || blocks.get(ResourceLocation.parse("tconstruct:piglin_wall_head"))!=net.minecraft.world.level.block.Blocks.PIGLIN_WALL_HEAD
      || items.get(ResourceLocation.parse("tconstruct:silky_jewel"))!=net.minecraft.world.item.Items.EMERALD
      || items.get(ResourceLocation.parse("tconstruct:piglin_head"))!=net.minecraft.world.item.Items.PIGLIN_HEAD) fail("legacy registry aliases");
    var gson=new slimeknights.tconstruct.library.utils.GsonLoadable<Value>(new com.google.gson.Gson(),Value.class);
    var nested=new slimeknights.tconstruct.library.json.field.OptionallyNestedLoadable<Value>(gson,"value");
    var value=new Value(42,"typed IDs");
    var json=gson.serialize(value);
    var wrapped=new com.google.gson.JsonObject();wrapped.add("value",json);
    if(!nested.convert(json,"test",TypedMap.EMPTY).equals(value) || !nested.convert(wrapped,"test",TypedMap.EMPTY).equals(value)) fail("nested JSON loading");
    var wire=new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      nested.encode(wire,value);
      if(!nested.decode(wire,TypedMap.EMPTY).equals(value) || wire.isReadable()) fail("GSON NBT roundtrip");
    } finally {wire.release();}
    var fresh=new slimeknights.tconstruct.library.json.NoFieldRecordLoadable<Object>(Object::new);
    var emptyJson=new com.google.gson.JsonObject();
    if(fresh.deserialize(emptyJson)==fresh.deserialize(emptyJson) || !fresh.serialize(new Object()).getAsJsonObject().isEmpty()) fail("fresh loader identity");
    var field=gson.<Value>requiredField("payload",java.util.function.Function.identity());
    var merged=new slimeknights.tconstruct.library.json.field.MergingField<Value,Value>(field,"nested",slimeknights.tconstruct.library.json.field.MergingField.MissingMode.CREATE);
    var mergedJson=new com.google.gson.JsonObject();
    merged.serializeInto(value,mergedJson,TypedMap.EMPTY);
    if(!merged.get(mergedJson,TypedMap.EMPTY).equals(value)) fail("merged field JSON");
    var listField=new slimeknights.tconstruct.library.json.field.MergingListField<Value,java.util.List<Value>>(field,"entries",java.util.function.Function.identity());
    var values=java.util.List.of(value,new Value(7,"second"));
    var listJson=new com.google.gson.JsonObject();
    var array=new com.google.gson.JsonArray();array.add(new com.google.gson.JsonObject());array.add(new com.google.gson.JsonObject());listJson.add("entries",array);
    listField.serializeInto(values,listJson,TypedMap.EMPTY);
    if(!listField.get(listJson,TypedMap.EMPTY).equals(values)) fail("merged list JSON");
    var fieldWire=new RegistryFriendlyByteBuf(Unpooled.buffer(),event.getServer().registryAccess());
    try {
      listField.encode(fieldWire,values,TypedMap.EMPTY);
      if(!listField.decode(fieldWire,TypedMap.EMPTY).equals(values) || fieldWire.isReadable()) fail("merged list wire");
    } finally {fieldWire.release();}
    System.out.println("TCONSTRUCT_TYPED_IDS_OK equality=1 hashing=1 validation=1 parsing=1 wire=1");
  }
  private static void fail(String reason) {throw new IllegalStateException(reason);}
}
