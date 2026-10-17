package slimeknights.tconstruct.library.recipe.fuel;

import javax.annotation.Nullable;
import java.util.Comparator;
import java.util.List;
import net.minecraft.world.item.crafting.RecipeHolder;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.material.Fluid;
import slimeknights.mantle.client.SafeClientAccess;

/** Reads the owning world's active recipes, so reload/removal cannot leave a constructor cache behind. */
public final class MeltingFuelLookup {
  private MeltingFuelLookup() {}
  private static List<RecipeHolder<MeltingFuel>> recipes(RecipeManager manager) {
    return manager.getAllRecipesFor(SmelteryFuelRecipes.TYPE.get()).stream()
      .sorted(Comparator.comparing(holder -> holder.id().toString())).toList();
  }
  @Nullable public static MeltingFuel findFuel(RecipeManager manager, Fluid fluid) {
    for (var holder : recipes(manager)) {
      var fuel = holder.value();
      if (fuel.getDuration() > 0 && fuel.getRate() > 0 && fuel.matches(fluid)) return fuel;
    }
    return null;
  }
  @Nullable public static MeltingFuel findFuel(Level level, Fluid fluid) {
    return level == null ? null : findFuel(level.getRecipeManager(), fluid);
  }
  @Nullable public static MeltingFuel getSolid(RecipeManager manager) {
    for (var holder : recipes(manager)) {
      var fuel = holder.value();
      if (fuel.isSolid() && fuel.getTemperature() > 0 && fuel.getRate() > 0) return fuel;
    }
    return null;
  }
  @Nullable public static MeltingFuel getSolid(Level level) { return level == null ? null : getSolid(level.getRecipeManager()); }
  public static boolean isFuel(Level level, Fluid fluid) { return findFuel(level, fluid) != null; }
  /** Client display adapters; server mechanics must always pass their owning level. */
  @Nullable public static MeltingFuel findFuel(Fluid fluid) { return findFuel(SafeClientAccess.getLevel(), fluid); }
  @Nullable public static MeltingFuel getSolid() { return getSolid(SafeClientAccess.getLevel()); }
}
