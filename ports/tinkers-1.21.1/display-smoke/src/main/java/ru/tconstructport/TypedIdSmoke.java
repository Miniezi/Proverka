package ru.tconstructport;
import io.netty.buffer.Unpooled;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import slimeknights.tconstruct.library.tools.stat.ToolStatId;
import slimeknights.mantle.util.typed.TypedMap;

final class TypedIdSmoke {
  static void validate() {
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
    var buf=new FriendlyByteBuf(Unpooled.buffer());
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
    System.out.println("TCONSTRUCT_TYPED_IDS_OK equality=1 hashing=1 validation=1 parsing=1 wire=1");
  }
  private static void fail(String reason) {throw new IllegalStateException(reason);}
}
