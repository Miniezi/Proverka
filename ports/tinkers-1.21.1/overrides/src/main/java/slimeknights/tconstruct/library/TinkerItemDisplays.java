package slimeknights.tconstruct.library;

import net.minecraft.world.item.ItemDisplayContext;

/** Tinkers display contexts, injected by NeoForge before enum class initialization. */
public final class TinkerItemDisplays {
  private TinkerItemDisplays() {}

  public static final ItemDisplayContext MELTER = ItemDisplayContext.valueOf("TCONSTRUCT_MELTER");
  public static final ItemDisplayContext TABLE = ItemDisplayContext.valueOf("TCONSTRUCT_TABLE");
  public static final ItemDisplayContext CASTING_TABLE = ItemDisplayContext.valueOf("TCONSTRUCT_CASTING_TABLE");
  public static final ItemDisplayContext CASTING_BASIN = ItemDisplayContext.valueOf("TCONSTRUCT_CASTING_BASIN");
  public static final ItemDisplayContext FLUID_CANNON = ItemDisplayContext.valueOf("TCONSTRUCT_FLUID_CANNON");
  public static final ItemDisplayContext THROWN = ItemDisplayContext.valueOf("TCONSTRUCT_THROWN");
}
