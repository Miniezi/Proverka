package ru.tconstructport;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeInput;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.Fluids;
import slimeknights.tconstruct.library.recipe.SingleItemContainer;
import slimeknights.tconstruct.library.recipe.input.TinkerSingleItemInput;
import slimeknights.tconstruct.library.recipe.casting.ICastingContainer;
import slimeknights.tconstruct.library.recipe.molding.IMoldingContainer;
import slimeknights.tconstruct.library.recipe.fuel.IFluidContainer;

final class RecipeInputSmoke {
  static void validate() {
    var single = new SingleItemContainer();
    check(single, 1, true);
    var stack = new ItemStack(Items.IRON_INGOT, 4);
    single.setStack(stack);
    check(single, 1, false);
    if(single.getItem()!=stack || single.getItem(0)!=stack || !single.getItem(1).isEmpty()) fail();
    // Recipe views must observe live inventory changes, not stale copies.
    TinkerSingleItemInput view = single::getStack;
    single.setStack(new ItemStack(Items.GOLD_INGOT));
    if(!view.getItem().is(Items.GOLD_INGOT) || view.getContainerSize()!=1) fail();
    ICastingContainer casting = new ICastingContainer() {
      public ItemStack getStack() { return single.getStack(); }
      public Fluid getFluid() { return Fluids.WATER; }
    };
    check(casting,1,false);
    if(casting.getFluid()!=Fluids.WATER || casting.getItem(0)!=single.getStack()) fail();
    var slots = new ItemStack[] {ItemStack.EMPTY,ItemStack.EMPTY};
    IMoldingContainer molding = new IMoldingContainer() {
      public ItemStack getMaterial() { return slots[0]; }
      public ItemStack getPattern() { return slots[1]; }
    };
    check(molding,2,true);
    slots[1]=new ItemStack(Items.STICK);
    check(molding,2,false);
    if(molding.getContainerSize()!=2 || molding.getItem(1)!=slots[1] || !molding.getItem(0).isEmpty()) fail();
    slots[0]=new ItemStack(Items.SAND);
    if(molding.getItem(0)!=slots[0] || !molding.getItem(2).isEmpty()) fail();
    IFluidContainer fuel = () -> Fluids.LAVA;
    check(fuel,0,true);
    if(fuel.getFluid()!=Fluids.LAVA || !fuel.getItem(0).isEmpty()) fail();
    System.out.println("TCONSTRUCT_RECIPE_INPUT_OK single=1 casting=1 molding_slots=2 fluid=1 live_views=1");
  }
  private static void check(RecipeInput input,int size,boolean empty) {
    if(input.size()!=size || input.isEmpty()!=empty) fail();
  }
  private static void fail() { throw new IllegalStateException("Recipe input size, slot order or live view changed"); }
}
