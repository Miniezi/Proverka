package ru.tconstructport;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.dispenser.BlockSource;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.DispenserBlock;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.entity.DispenserBlockEntity;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.shared.block.PlaceBlockDispenserBehavior;

final class DispenserSmoke {
  static void validate(ServerStartedEvent event) {
    var level = event.getServer().overworld();
    var pos = new BlockPos(0, 200, 0);
    var target = pos.relative(Direction.EAST);
    level.setBlockAndUpdate(pos, Blocks.DISPENSER.defaultBlockState().setValue(DispenserBlock.FACING, Direction.EAST));
    level.setBlockAndUpdate(target, Blocks.AIR.defaultBlockState());
    try {
      var source = new BlockSource(level, pos, level.getBlockState(pos), (DispenserBlockEntity)level.getBlockEntity(pos));
      var behavior = PlaceBlockDispenserBehavior.INSTANCE;
      var stone = new ItemStack(Items.STONE, 2);
      behavior.dispense(source, stone);
      if (!level.getBlockState(target).is(Blocks.STONE) || stone.getCount() != 1) fail("placement consumption");
      behavior.dispense(source, stone);
      if (stone.getCount() != 1 || !level.getBlockState(target).is(Blocks.STONE)) fail("blocked placement consumed item");
      level.setBlockAndUpdate(target, Blocks.AIR.defaultBlockState());
      var chest = new ItemStack(Items.CHEST, 2);
      chest.set(DataComponents.CUSTOM_NAME, Component.literal("Dispenser component test"));
      behavior.dispense(source, chest);
      if (chest.getCount() != 1 || !(level.getBlockEntity(target) instanceof ChestBlockEntity entity)
          || !entity.getName().getString().equals("Dispenser component test")) fail("placed components");
      level.setBlockAndUpdate(target, Blocks.AIR.defaultBlockState());
      var stick = new ItemStack(Items.STICK, 2);
      behavior.dispense(source, stick);
      if (stick.getCount() != 2 || !level.isEmptyBlock(target)) fail("nonblock consumed");
    } finally {
      level.removeBlock(target, false);
      level.removeBlock(pos, false);
    }
    System.out.println("TCONSTRUCT_DISPENSER_OK placement=1 consumption=1 blocked=1 components=1");
  }
  private static void fail(String message) { throw new IllegalStateException(message); }
}
