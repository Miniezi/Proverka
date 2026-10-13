package slimeknights.tconstruct.common.registration;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.registries.ModifyRegistriesEvent;
/** Historical names resolve to current IDs without eagerly resolving deferred items. */
public final class TinkerRegistryAliases {
  private TinkerRegistryAliases() {}
  private static ResourceLocation id(String path) {return ResourceLocation.fromNamespaceAndPath("tconstruct",path);}
  public static void register(ModifyRegistriesEvent event) {
    var blocks=event.getRegistry(Registries.BLOCK);
    blocks.addAlias(id("silky_jewel_block"), ResourceLocation.withDefaultNamespace("emerald_block"));
    blocks.addAlias(id("piglin_head"), ResourceLocation.withDefaultNamespace("piglin_head"));
    blocks.addAlias(id("piglin_wall_head"), ResourceLocation.withDefaultNamespace("piglin_wall_head"));
    var items=event.getRegistry(Registries.ITEM);
    items.addAlias(id("silky_jewel"),ResourceLocation.withDefaultNamespace("emerald"));
    items.addAlias(id("silky_jewel_block"),ResourceLocation.withDefaultNamespace("emerald_block"));
    items.addAlias(id("piglin_head"),ResourceLocation.withDefaultNamespace("piglin_head"));
    items.addAlias(id("round_plate"),id("adze_head"));
    items.addAlias(id("round_plate_cast"),id("adze_head_cast"));
    items.addAlias(id("round_plate_sand_cast"),id("adze_head_sand_cast"));
    items.addAlias(id("round_plate_red_sand_cast"),id("adze_head_red_sand_cast"));
    items.addAlias(id("slime_chestplate"),id("slime_wings"));
  }
}
