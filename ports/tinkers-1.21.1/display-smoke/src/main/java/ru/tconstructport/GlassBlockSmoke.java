package ru.tconstructport;

import com.mojang.serialization.JsonOps;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.shared.block.*;

final class GlassBlockSmoke {
  static void validate(ServerStartedEvent event) {
    var level = event.getServer().overworld();
    for (var color : ClearStainedGlassBlock.GlassColor.values()) {
      var block = new ClearStainedGlassBlock(BlockBehaviour.Properties.of().noOcclusion(), color);
      var pane = new ClearStainedGlassPaneBlock(BlockBehaviour.Properties.of().noOcclusion(), color);
      int expected = 0xFF000000 | color.getColor();
      if (block.getBeaconColorMultiplier(block.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected
          || pane.getBeaconColorMultiplier(pane.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected) fail("beacon color");
      var encoded = ClearStainedGlassBlock.CODEC.codec().encodeStart(JsonOps.INSTANCE, block).getOrThrow();
      var decoded = ClearStainedGlassBlock.CODEC.codec().parse(JsonOps.INSTANCE, encoded).getOrThrow();
      if (decoded.getBeaconColorMultiplier(decoded.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected) fail("block color codec");
      var paneJson = ClearStainedGlassPaneBlock.CODEC.codec().encodeStart(JsonOps.INSTANCE, pane).getOrThrow();
      var decodedPane = ClearStainedGlassPaneBlock.CODEC.codec().parse(JsonOps.INSTANCE, paneJson).getOrThrow();
      if (decodedPane.getBeaconColorMultiplier(decodedPane.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected) fail("pane color codec");
      if (!block.skipRendering(block.defaultBlockState(), block.defaultBlockState(), Direction.NORTH)) fail("glass culling");
    }
    var soul = SoulGlassBlock.CODEC.codec().parse(JsonOps.INSTANCE, SoulGlassBlock.CODEC.codec()
      .encodeStart(JsonOps.INSTANCE, new SoulGlassBlock(BlockBehaviour.Properties.of().noCollission())).getOrThrow()).getOrThrow();
    for (var path : PathComputationType.values()) if (soul.isPathfindable(soul.defaultBlockState(), path)) fail("soul pathfinding");
    if (soul.getBlockSupportShape(soul.defaultBlockState(), level, BlockPos.ZERO).isEmpty()) fail("soul support");
    var pane = BetterPaneBlock.CODEC.codec().parse(JsonOps.INSTANCE, BetterPaneBlock.CODEC.codec()
      .encodeStart(JsonOps.INSTANCE, new BetterPaneBlock(BlockBehaviour.Properties.of())).getOrThrow()).getOrThrow();
    var state = pane.defaultBlockState().setValue(BetterPaneBlock.NORTH, true);
    if (!pane.skipRendering(state, state, Direction.UP)
        || pane.skipRendering(state, state.setValue(BetterPaneBlock.NORTH, false), Direction.UP)) fail("pane culling");
    ClearGlassPaneBlock.CODEC.codec().parse(JsonOps.INSTANCE, ClearGlassPaneBlock.CODEC.codec()
      .encodeStart(JsonOps.INSTANCE, new ClearGlassPaneBlock(BlockBehaviour.Properties.of())).getOrThrow()).getOrThrow();
    System.out.println("TCONSTRUCT_GLASS_BLOCKS_OK colors=16 codecs=5 culling=1 soul=1");
  }
  private static void fail(String message) { throw new IllegalStateException(message); }
}
