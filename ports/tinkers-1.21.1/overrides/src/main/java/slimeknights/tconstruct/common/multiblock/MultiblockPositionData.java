package slimeknights.tconstruct.common.multiblock;

import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.IntArrayTag;
import net.minecraft.nbt.Tag;

/** Current position arrays and legacy X/Y/Z compounds used by saved multiblocks. */
public final class MultiblockPositionData {
  private MultiblockPositionData() {}
  @Nullable
  public static BlockPos read(@Nullable Tag tag) {
    if (tag instanceof IntArrayTag array) {
      int[] xyz = array.getAsIntArray();
      return xyz.length == 3 ? new BlockPos(xyz[0], xyz[1], xyz[2]) : null;
    }
    if (tag instanceof CompoundTag compound && compound.contains("X", Tag.TAG_ANY_NUMERIC)
        && compound.contains("Y", Tag.TAG_ANY_NUMERIC) && compound.contains("Z", Tag.TAG_ANY_NUMERIC)) {
      return new BlockPos(compound.getInt("X"), compound.getInt("Y"), compound.getInt("Z"));
    }
    return null;
  }
}
