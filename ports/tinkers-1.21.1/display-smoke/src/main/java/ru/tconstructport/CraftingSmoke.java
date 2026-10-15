package ru.tconstructport;

import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.SingleRecipeInput;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.tables.block.entity.inventory.CraftingContainerWrapper;

final class CraftingSmoke {
  static void validate(ServerStartedEvent event) {
    var level=event.getServer().overworld();
    var manager=level.getRecipeManager();
    var inventory=new SimpleContainer(9);
    var wrapper=new CraftingContainerWrapper(inventory,3,3);
    if(!wrapper.asRecipeInput().isEmpty()) fail("empty grid");
    // Shape in bottom-right must match after trimming unused rows and columns.
    for(int index:new int[]{4,5,7,8}) inventory.setItem(index,new ItemStack(Items.OAK_PLANKS));
    var input=wrapper.asRecipeInput();
    if(input.width()!=2 || input.height()!=2) fail("trimmed dimensions");
    var shaped=manager.getRecipeFor(RecipeType.CRAFTING,input,level).orElseThrow().value();
    if(!shaped.assemble(input,level.registryAccess()).is(Items.CRAFTING_TABLE)) fail("shifted shaped recipe");
    inventory.clearContent();
    if(shaped.matches(wrapper.asRecipeInput(),level)) fail("stale cached recipe accepted empty grid");
    // A one-slot shapeless recipe returns a bottle in the original bottom-right slot.
    inventory.setItem(8,new ItemStack(Items.HONEY_BOTTLE));
    input=wrapper.asRecipeInput();
    var shapeless=manager.getRecipeFor(RecipeType.CRAFTING,input,level).orElseThrow().value();
    var output=shapeless.assemble(input,level.registryAccess());
    if(!output.is(Items.SUGAR) || output.getCount()!=3) fail("shapeless output");
    var remaining=wrapper.recipeRemainders(shapeless);
    if(remaining.size()!=9 || !remaining.get(8).is(Items.GLASS_BOTTLE)) fail("remainder offset");
    for(int i=0;i<8;i++) if(!remaining.get(i).isEmpty()) fail("remainder moved to wrong slot");
    if(!inventory.getItem(8).is(Items.HONEY_BOTTLE)) fail("recipe lookup mutated inventory");
    var ore=new SingleRecipeInput(new ItemStack(Items.RAW_IRON));
    var smelting=manager.getRecipeFor(RecipeType.SMELTING,ore,level).orElseThrow().value();
    if(!smelting.assemble(ore,level.registryAccess()).is(Items.IRON_INGOT)) fail("smelting input");
    if(manager.getRecipeFor(RecipeType.SMELTING,new SingleRecipeInput(new ItemStack(Items.STICK)),level).isPresent()) fail("invalid smelting input");
    // Use a separate manager: reload checks must not replace the server's recipes.
    var isolated = new net.minecraft.world.item.crafting.RecipeManager(level.registryAccess());
    var ironHolder = manager.getRecipeFor(RecipeType.SMELTING, ore, level).orElseThrow();
    var goldInput = new SingleRecipeInput(new ItemStack(Items.RAW_GOLD));
    var goldHolder = manager.getRecipeFor(RecipeType.SMELTING, goldInput, level).orElseThrow();
    isolated.replaceRecipes(java.util.List.of(ironHolder));
    if (isolated.getRecipeFor(RecipeType.SMELTING, ore, level, ironHolder.id()).orElseThrow().value() != ironHolder.value()) fail("cached ID lookup");
    var replacement = new net.minecraft.world.item.crafting.RecipeHolder<>(ironHolder.id(), goldHolder.value());
    isolated.replaceRecipes(java.util.List.of(replacement));
    if (isolated.getRecipeFor(RecipeType.SMELTING, ore, level, ironHolder.id()).isPresent()) fail("stale recipe after reload");
    if (isolated.getRecipeFor(RecipeType.SMELTING, goldInput, level, ironHolder.id()).orElseThrow().value() != goldHolder.value()) fail("reloaded recipe not used");
    isolated.replaceRecipes(java.util.List.of());
    if (isolated.getRecipeFor(RecipeType.SMELTING, goldInput, level, ironHolder.id()).isPresent()) fail("removed recipe still cached");
    System.out.println("TCONSTRUCT_RECIPE_ID_CACHE_OK lookup=1 replacement=1 removal=1");
    System.out.println("TCONSTRUCT_CRAFTING_OK shifted_shape=1 remainder_offset=1 smelting=1 no_mutation=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
