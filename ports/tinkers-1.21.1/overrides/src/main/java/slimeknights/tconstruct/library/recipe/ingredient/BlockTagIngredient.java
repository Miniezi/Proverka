package slimeknights.tconstruct.library.recipe.ingredient;

import com.mojang.serialization.MapCodec;
import java.util.stream.Stream;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Block;
import net.neoforged.neoforge.common.crafting.ICustomIngredient;
import net.neoforged.neoforge.common.crafting.IngredientType;
import slimeknights.mantle.util.RegistryHelper;

/** Matches item forms of tagged blocks, including blocks that share an item form. */
public record BlockTagIngredient(TagKey<Block> tag) implements ICustomIngredient {
  public static final ResourceLocation ID = ResourceLocation.fromNamespaceAndPath("tconstruct","block_tag");
  public static final MapCodec<BlockTagIngredient> CODEC = TagKey.codec(Registries.BLOCK).fieldOf("tag").xmap(BlockTagIngredient::new,BlockTagIngredient::tag);
  public static final IngredientType<BlockTagIngredient> TYPE = new IngredientType<>(CODEC);
  private Stream<Item> items() {
    return RegistryHelper.getTagValueStream(BuiltInRegistries.BLOCK,tag).map(Block::asItem).filter(item -> item != Items.AIR).distinct();
  }
  @Override public boolean test(ItemStack stack) { return stack != null && !stack.isEmpty() && items().anyMatch(item -> item == stack.getItem()); }
  @Override public Stream<ItemStack> getItems() { return items().map(ItemStack::new); }
  @Override public boolean isSimple() { return true; }
  @Override public IngredientType<?> getType() { return TYPE; }
}
