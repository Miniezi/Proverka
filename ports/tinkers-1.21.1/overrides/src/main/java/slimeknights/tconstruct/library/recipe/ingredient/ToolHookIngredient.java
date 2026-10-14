package slimeknights.tconstruct.library.recipe.ingredient;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.common.crafting.ICustomIngredient;
import net.neoforged.neoforge.common.crafting.IngredientType;
import slimeknights.mantle.data.loadable.LoadableCodec;
import slimeknights.tconstruct.common.TinkerTags;
import slimeknights.tconstruct.library.module.ModuleHook;
import slimeknights.tconstruct.library.tools.definition.module.ToolHooks;
import slimeknights.tconstruct.library.tools.item.IModifiable;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;

/** Tests the current tool definition instead of caching a set of matching item IDs. */
public record ToolHookIngredient(TagKey<Item> tag, ModuleHook<?> hook) implements ICustomIngredient {
  public static final ResourceLocation ID = ResourceLocation.fromNamespaceAndPath("tconstruct", "tool_hook");
  public static final MapCodec<ToolHookIngredient> CODEC = RecordCodecBuilder.mapCodec(instance -> instance.group(
    TagKey.codec(Registries.ITEM).optionalFieldOf("tag", TinkerTags.Items.MODIFIABLE).forGetter(ToolHookIngredient::tag),
    new LoadableCodec<>(ToolHooks.LOADER).fieldOf("hook").forGetter(ToolHookIngredient::hook)
  ).apply(instance, ToolHookIngredient::new));
  public static final IngredientType<ToolHookIngredient> TYPE = new IngredientType<>(CODEC);
  public static Ingredient of(TagKey<Item> tag, ModuleHook<?> hook) {
    return new ToolHookIngredient(tag, hook).toVanilla();
  }
  public static Ingredient of(ModuleHook<?> hook) { return of(TinkerTags.Items.MODIFIABLE, hook); }
  @Override public boolean test(ItemStack stack) {
    return stack != null && !stack.isEmpty() && stack.is(tag)
      && stack.getItem() instanceof IModifiable modifiable
      && modifiable.getToolDefinition().getData().getHooks().hasHook(hook);
  }
  @Override public Stream<ItemStack> getItems() {
    return StreamSupport.stream(BuiltInRegistries.ITEM.getTagOrEmpty(tag).spliterator(), false)
      .map(holder -> new ItemStack(holder.value())).filter(this::test);
  }
  @Override public boolean isSimple() { return false; }
  @Override public IngredientType<?> getType() { return TYPE; }
}
