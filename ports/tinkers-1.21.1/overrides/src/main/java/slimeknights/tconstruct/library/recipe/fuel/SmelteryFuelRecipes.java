package slimeknights.tconstruct.library.recipe.fuel;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import slimeknights.mantle.recipe.helper.LoadableRecipeSerializer;

/** Shared production fuel registration, usable without initializing every smeltery block. */
public final class SmelteryFuelRecipes {
  private SmelteryFuelRecipes() {}
  private static final DeferredRegister<RecipeType<?>> TYPES = DeferredRegister.create(Registries.RECIPE_TYPE, "tconstruct");
  private static final DeferredRegister<RecipeSerializer<?>> SERIALIZERS = DeferredRegister.create(Registries.RECIPE_SERIALIZER, "tconstruct");
  public static final DeferredHolder<RecipeType<?>,RecipeType<MeltingFuel>> TYPE = TYPES.register("fuel", () -> new RecipeType<>() {
    @Override public String toString() { return "tconstruct:fuel"; }
  });
  public static final DeferredHolder<RecipeSerializer<?>,RecipeSerializer<MeltingFuel>> SERIALIZER =
    SERIALIZERS.register("melting_fuel", () -> LoadableRecipeSerializer.of(MeltingFuel.LOADER));
  public static void register(IEventBus bus) { TYPES.register(bus); SERIALIZERS.register(bus); }
}
