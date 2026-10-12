package slimeknights.tconstruct.common.network;
import java.util.Optional;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeManager;
/** Resolves the server-owned recipe ID while legacy tables still cache recipe values. */
public final class RecipeNetworkLookup {
  private RecipeNetworkLookup() {}
  public static Optional<ResourceLocation> findId(RecipeManager manager, Recipe<?> recipe) {
    return manager.getRecipes().stream().filter(holder -> holder.value()==recipe).map(holder -> holder.id()).findFirst();
  }
}
