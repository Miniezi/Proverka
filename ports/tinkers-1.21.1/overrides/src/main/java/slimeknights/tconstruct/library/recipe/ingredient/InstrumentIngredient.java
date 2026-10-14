package slimeknights.tconstruct.library.recipe.ingredient;

import com.mojang.serialization.DataResult;
import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Instrument;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ItemLike;
import net.neoforged.neoforge.common.crafting.ICustomIngredient;
import net.neoforged.neoforge.common.crafting.IngredientType;
import java.util.Optional;
import java.util.stream.Stream;

/** Matches the instrument component, including recipes excluding an instrument tag. */
public record InstrumentIngredient(Item item, Optional<ResourceKey<Instrument>> instrument,
                                   Optional<TagKey<Instrument>> ignore) implements ICustomIngredient {
  public static final ResourceLocation ID = ResourceLocation.fromNamespaceAndPath("tconstruct", "instrument");
  private static final MapCodec<InstrumentIngredient> FIELDS = RecordCodecBuilder.mapCodec(instance -> instance.group(
    BuiltInRegistries.ITEM.byNameCodec().fieldOf("item").forGetter(InstrumentIngredient::item),
    ResourceKey.codec(Registries.INSTRUMENT).optionalFieldOf("instrument").forGetter(InstrumentIngredient::instrument),
    TagKey.codec(Registries.INSTRUMENT).optionalFieldOf("ignore").forGetter(InstrumentIngredient::ignore)
  ).apply(instance, InstrumentIngredient::new));
  public static final MapCodec<InstrumentIngredient> CODEC = FIELDS.validate(value ->
    value.item == Items.AIR || value.instrument.isPresent() == value.ignore.isPresent()
      ? DataResult.error(() -> "Instrument ingredient requires a non-air item and exactly one of instrument or ignore")
      : DataResult.success(value));
  public static final IngredientType<InstrumentIngredient> TYPE = new IngredientType<>(CODEC);

  public static Ingredient of(ItemLike item, ResourceKey<Instrument> instrument) {
    return new InstrumentIngredient(item.asItem(), Optional.of(instrument), Optional.empty()).toVanilla();
  }
  public static Ingredient of(ItemLike item, TagKey<Instrument> ignore) {
    return new InstrumentIngredient(item.asItem(), Optional.empty(), Optional.of(ignore)).toVanilla();
  }
  @Override public boolean test(ItemStack stack) {
    if (stack == null || stack.isEmpty() || !stack.is(item)) return false;
    var holder = stack.get(DataComponents.INSTRUMENT);
    if (instrument.isPresent()) return holder != null && holder.is(instrument.get());
    return ignore.isPresent() && (holder == null || !holder.is(ignore.get()));
  }
  @Override public Stream<ItemStack> getItems() {
    if (instrument.isPresent()) {
      return BuiltInRegistries.INSTRUMENT.getHolder(instrument.get()).stream().map(holder -> {
        var stack = new ItemStack(item);
        stack.set(DataComponents.INSTRUMENT, holder);
        return stack;
      });
    }
    var empty = new ItemStack(item);
    empty.remove(DataComponents.INSTRUMENT);
    return Stream.concat(Stream.of(empty), BuiltInRegistries.INSTRUMENT.holders().map(holder -> {
      var stack = new ItemStack(item);
      stack.set(DataComponents.INSTRUMENT, holder);
      return stack;
    })).filter(this::test);
  }
  @Override public boolean isSimple() { return false; }
  @Override public IngredientType<?> getType() { return TYPE; }
}
