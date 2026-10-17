package slimeknights.tconstruct.library.recipe.fuel;

import java.util.List;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import net.neoforged.neoforge.fluids.FluidStack;
import slimeknights.mantle.data.loadable.primitive.IntLoadable;
import slimeknights.mantle.data.loadable.record.RecordLoadable;
import slimeknights.mantle.recipe.ICustomOutputRecipe;
import slimeknights.tconstruct.library.recipe.ingredient.FluidIngredient;

/** A manager-owned fuel recipe. Construction and codec decoding do not register global recipes. */
public final class MeltingFuel implements ICustomOutputRecipe<IFluidContainer> {
  public static final RecordLoadable<MeltingFuel> LOADER = RecordLoadable.create(
    FluidIngredient.LOADABLE.defaultField("fluid", FluidIngredient.EMPTY, MeltingFuel::getInput),
    IntLoadable.FROM_ONE.defaultField("duration", 0, MeltingFuel::getDuration),
    IntLoadable.FROM_ONE.requiredField("temperature", MeltingFuel::getTemperature),
    IntLoadable.FROM_ONE.requiredField("rate", MeltingFuel::getRate),
    MeltingFuel::new).validate((fuel, error) -> {
      if (!fuel.isSolid() && fuel.duration == 0) throw error.create("Missing JSON field duration");
      return fuel;
    });

  private final FluidIngredient input;
  private final int duration;
  private final int temperature;
  private final int rate;
  public MeltingFuel(FluidIngredient input, int duration, int temperature, int rate) {
    this.input = java.util.Objects.requireNonNull(input);
    this.duration = duration;
    this.temperature = temperature;
    this.rate = rate;
  }
  public FluidIngredient getInput() { return input; }
  public int getDuration() { return duration; }
  public int getTemperature() { return temperature; }
  public int getRate() { return rate; }
  public boolean isSolid() { return input == FluidIngredient.EMPTY || input.test(Fluids.EMPTY); }
  public boolean matches(Fluid fluid) { return !isSolid() && fluid != Fluids.EMPTY && input.test(fluid); }
  @Override public boolean matches(IFluidContainer input, Level level) { return matches(input.getFluid()); }
  public int getAmount(IFluidContainer input) { return getAmount(input.getFluid()); }
  public int getAmount(Fluid fluid) { return matches(fluid) ? input.getAmount(fluid) : 0; }
  public List<FluidStack> getInputs() { return input.getFluids(); }
  @Override public RecipeType<?> getType() { return SmelteryFuelRecipes.TYPE.get(); }
  @Override public RecipeSerializer<?> getSerializer() { return SmelteryFuelRecipes.SERIALIZER.get(); }
  @Override public ItemStack getToastSymbol() {
    return new ItemStack(BuiltInRegistries.ITEM.get(ResourceLocation.fromNamespaceAndPath("tconstruct", "seared_fuel_tank")));
  }
}
