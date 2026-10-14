package slimeknights.tconstruct.library.tools.nbt;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Optional;

/** Detached inventory edits suitable for publishing as immutable item components. */
public final class ToolInventoryData {
  public static final String SLOT = "Slot";
  private ToolInventoryData() {}

  /** Replace/remove a slot without mutating the source or retaining replacement aliases. */
  public static ListTag set(ListTag source, int slot, CompoundTag replacement) {
    if (slot < 0) throw new IllegalArgumentException("Negative inventory slot");
    ListTag result = source.copy();
    int insertion = 0;
    for (int i = 0; i < result.size(); i++) {
      int stored = result.getCompound(i).getInt(SLOT);
      if (stored == slot) {
        if (replacement == null) result.remove(i);
        else {
          CompoundTag item = replacement.copy();
          item.putInt(SLOT, slot);
          result.set(i, item);
        }
        return result;
      }
      if (stored < slot) insertion = i+1;
    }
    if (replacement != null) {
      CompoundTag item = replacement.copy();
      item.putInt(SLOT, slot);
      result.add(insertion, item);
    }
    return result;
  }

  /** Preserve valid slots and relocate invalid/duplicate indices atomically, or reject. */
  public static Optional<ListTag> fit(ListTag source, int capacity) {
    if (capacity < 0 || source.size() > capacity || (!source.isEmpty() && source.getElementType()!=Tag.TAG_COMPOUND)) return Optional.empty();
    ListTag result = source.copy();
    var occupied = new HashSet<Integer>();
    var move = new ArrayList<CompoundTag>();
    for (int i = 0; i < result.size(); i++) {
      CompoundTag entry = result.getCompound(i);
      int slot = entry.getInt(SLOT);
      if (!entry.contains(SLOT, Tag.TAG_ANY_NUMERIC) || slot < 0 || slot >= capacity || !occupied.add(slot)) move.add(entry);
    }
    int free = 0;
    for (CompoundTag entry : move) {
      while (occupied.contains(free)) free++;
      if (free >= capacity) return Optional.empty();
      entry.putInt(SLOT, free);
      occupied.add(free);
    }
    return Optional.of(result);
  }
}
