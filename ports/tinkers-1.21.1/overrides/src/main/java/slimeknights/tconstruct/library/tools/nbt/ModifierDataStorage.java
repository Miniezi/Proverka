package slimeknights.tconstruct.library.tools.nbt;

import net.minecraft.nbt.CompoundTag;
import java.util.Objects;
import java.util.function.Consumer;

/** Mutable working data with explicit snapshot publication for component-backed owners. */
public final class ModifierDataStorage {
  private final CompoundTag data;
  private final Consumer<CompoundTag> publish;

  public ModifierDataStorage(CompoundTag data, Consumer<CompoundTag> publish) {
    this.data = Objects.requireNonNull(data);
    this.publish = publish;
  }

  /** Publishes an isolated snapshot, never the live compound owned by the tool. */
  public void changed() { if (publish != null) publish.accept(data.copy()); }

  /** Replace while retaining the working compound identity. Self-copy is safe. */
  public void replace(CompoundTag replacement) {
    CompoundTag snapshot = replacement.copy();
    data.getAllKeys().clear();
    data.merge(snapshot);
    changed();
  }

  /** Nested edits publish once; exceptions before commit leave working data untouched. */
  public void edit(Consumer<CompoundTag> edit) {
    CompoundTag snapshot = data.copy();
    edit.accept(snapshot);
    replace(snapshot);
  }
}
