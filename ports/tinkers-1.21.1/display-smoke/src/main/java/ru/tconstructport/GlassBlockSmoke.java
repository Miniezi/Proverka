package ru.tconstructport;

import com.mojang.serialization.JsonOps;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.pathfinder.PathComputationType;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.shared.block.*;

final class GlassBlockSmoke {
  private static net.neoforged.neoforge.registries.RegisterEvent registration;
  private static int nextId;
  private static boolean passed;
  static void init(net.neoforged.bus.api.IEventBus bus) {
    bus.addListener((net.neoforged.neoforge.registries.RegisterEvent event) -> {
      if (event.getRegistryKey().equals(net.minecraft.core.registries.Registries.BLOCK)) {
        registration = event;
        checkBlocks();
        registration = null;
        passed = true;
      }
    });
  }
  private static <T extends net.minecraft.world.level.block.Block> T keep(T block) {
    registration.register(net.minecraft.core.registries.Registries.BLOCK,
      net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("tconstruct", "glass_fixture_" + nextId++), () -> block);
    return block;
  }
  static void validate(ServerStartedEvent event) {
    if (!passed) fail("registration checks did not run");
    System.out.println("TCONSTRUCT_GLASS_BLOCKS_OK colors=16 codecs=5 culling=1 soul=1");
  }
  private static void checkBlocks() {
    net.minecraft.world.level.LevelReader level = null;
    for (var color : ClearStainedGlassBlock.GlassColor.values()) {
      var block = keep(new ClearStainedGlassBlock(BlockBehaviour.Properties.of().noOcclusion(), color));
      var pane = keep(new ClearStainedGlassPaneBlock(BlockBehaviour.Properties.of().noOcclusion(), color));
      int expected = 0xFF000000 | color.getColor();
      if (block.getBeaconColorMultiplier(block.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected
          || pane.getBeaconColorMultiplier(pane.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected) fail("beacon color");
      var encoded = ClearStainedGlassBlock.CODEC.codec().encodeStart(JsonOps.INSTANCE, block).getOrThrow();
      var decoded = keep(ClearStainedGlassBlock.CODEC.codec().parse(JsonOps.INSTANCE, encoded).getOrThrow());
      if (decoded.getBeaconColorMultiplier(decoded.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected) fail("block color codec");
      var paneJson = ClearStainedGlassPaneBlock.CODEC.codec().encodeStart(JsonOps.INSTANCE, pane).getOrThrow();
      var decodedPane = keep(ClearStainedGlassPaneBlock.CODEC.codec().parse(JsonOps.INSTANCE, paneJson).getOrThrow());
      if (decodedPane.getBeaconColorMultiplier(decodedPane.defaultBlockState(), level, BlockPos.ZERO, BlockPos.ZERO) != expected) fail("pane color codec");
      if (!block.defaultBlockState().skipRendering(block.defaultBlockState(), Direction.NORTH)) fail("glass culling");
    }
    var soul = keep(SoulGlassBlock.CODEC.codec().parse(JsonOps.INSTANCE, SoulGlassBlock.CODEC.codec()
      .encodeStart(JsonOps.INSTANCE, keep(new SoulGlassBlock(BlockBehaviour.Properties.of().noCollission()))).getOrThrow()).getOrThrow());
    for (var path : PathComputationType.values()) if (soul.isPathfindable(soul.defaultBlockState(), path)) fail("soul pathfinding");
    if (soul.getBlockSupportShape(soul.defaultBlockState(), level, BlockPos.ZERO).isEmpty()) fail("soul support");
    var pane = keep(BetterPaneBlock.CODEC.codec().parse(JsonOps.INSTANCE, BetterPaneBlock.CODEC.codec()
      .encodeStart(JsonOps.INSTANCE, keep(new BetterPaneBlock(BlockBehaviour.Properties.of()))).getOrThrow()).getOrThrow());
    var state = pane.defaultBlockState().setValue(BetterPaneBlock.NORTH, true);
    if (!pane.skipRendering(state, state, Direction.UP)
        || pane.skipRendering(state, state.setValue(BetterPaneBlock.NORTH, false), Direction.UP)) fail("pane culling");
    keep(ClearGlassPaneBlock.CODEC.codec().parse(JsonOps.INSTANCE, ClearGlassPaneBlock.CODEC.codec()
      .encodeStart(JsonOps.INSTANCE, keep(new ClearGlassPaneBlock(BlockBehaviour.Properties.of()))).getOrThrow()).getOrThrow());

  }
  private static void fail(String message) { throw new IllegalStateException(message); }
}
