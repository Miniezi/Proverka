package ru.tconstructport;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.nbt.Tag;
import slimeknights.tconstruct.library.utils.RestrictedCompoundTag;

final class RestrictedDataSmoke {
  static void validate() {
    CompoundTag root = new CompoundTag();
    root.putInt("protected", 42);
    var keys = new java.util.HashSet<String>(); keys.add("protected");
    var published = new java.util.ArrayList<CompoundTag>();
    var view = new RestrictedCompoundTag(root, keys, published::add);
    keys.clear();
    view.putInt("protected", 0); view.remove("protected");
    if (root.getInt("protected") != 42 || view.contains("protected", Tag.TAG_INT)
        || view.getInt("protected") != 0 || view.get("protected") != null || !published.isEmpty()) fail("restricted access");
    CompoundTag child = new CompoundTag(); child.putInt("value", 3);
    view.put("child", child); child.putInt("value", 9);
    view.getCompound("child").putInt("value", 8);
    ((CompoundTag)view.get("child")).putInt("value", 7);
    if (root.getCompound("child").getInt("value") != 3) fail("compound aliases");
    var list = new ListTag(); list.add(StringTag.valueOf("first"));
    view.put("list", list); list.clear(); view.getList("list", Tag.TAG_STRING).clear();
    if (root.getList("list", Tag.TAG_STRING).size() != 1) fail("list aliases");
    published.get(0).getCompound("child").putInt("value", 99);
    if (root.getCompound("child").getInt("value") != 3) fail("published aliases");
    int count = published.size();
    RestrictedCompoundTag[] retained = new RestrictedCompoundTag[1];
    view.edit(edit -> {
      retained[0] = edit;
      edit.putBoolean("enabled", true); edit.putFloat("strength", 1.5f);
      edit.putString("name", "test"); edit.putInt("protected", -1); edit.remove("list");
    });
    retained[0].putString("name", "late mutation");
    if (published.size() != count + 1 || !view.getBoolean("enabled") || view.getFloat("strength") != 1.5f
        || !view.getString("name").equals("test") || root.contains("list") || root.getInt("protected") != 42) fail("transaction");
    CompoundTag before = root.copy(); count = published.size();
    try {
      view.edit(edit -> { edit.remove("child"); throw new IllegalArgumentException("abort"); });
      fail("exception missing");
    } catch (IllegalArgumentException expected) {}
    if (!root.equals(before) || published.size() != count) fail("rollback");
    System.out.println("TCONSTRUCT_RESTRICTED_DATA_OK protection=1 isolation=1 publication=1 atomic=1");
  }
  private static void fail(String message) { throw new IllegalStateException(message); }
}
