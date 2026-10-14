package ru.tconstructport;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import slimeknights.tconstruct.library.tools.nbt.ToolInventoryData;

final class ToolInventoryDataSmoke {
  private static CompoundTag entry(int slot, String id) {
    var tag = new CompoundTag(); tag.putInt("Slot",slot); tag.putString("id",id); return tag;
  }
  static void validate() {
    var original = new ListTag(); original.add(entry(0,"a")); original.add(entry(3,"b"));
    var replacement = entry(99,"c");
    var inserted = ToolInventoryData.set(original,1,replacement);
    replacement.putString("id","changed");
    if (original.size()!=2 || inserted.size()!=3 || inserted.getCompound(1).getInt("Slot")!=1
        || !inserted.getCompound(1).getString("id").equals("c")) fail("insert isolation");
    var replaced = ToolInventoryData.set(inserted,1,entry(1,"d"));
    if (replaced.size()!=3 || !replaced.getCompound(1).getString("id").equals("d")
        || !inserted.getCompound(1).getString("id").equals("c")) fail("replace");
    if (ToolInventoryData.set(replaced,1,null).size()!=2 || ToolInventoryData.set(replaced,8,null).size()!=3) fail("remove");
    var fitted = ToolInventoryData.fit(original,2).orElseThrow();
    if (fitted.getCompound(1).getInt("Slot")!=1 || original.getCompound(1).getInt("Slot")!=3) fail("relocation isolation");
    var invalid = new ListTag(); invalid.add(entry(-1,"a")); invalid.add(entry(0,"b")); invalid.add(entry(0,"c"));
    var repaired = ToolInventoryData.fit(invalid,3).orElseThrow();
    var used = new java.util.HashSet<Integer>();
    for (int i=0;i<repaired.size();i++) {
      int slot=repaired.getCompound(i).getInt("Slot");
      if (slot<0 || slot>=3 || !used.add(slot)) fail("invalid slot repair");
    }
    var saved = invalid.copy();
    if (ToolInventoryData.fit(invalid,2).isPresent() || !invalid.equals(saved)
        || ToolInventoryData.fit(original,0).isPresent() || ToolInventoryData.fit(original,-1).isPresent()) fail("atomic rejection");
    if (ToolInventoryData.fit(new ListTag(),0).isEmpty()) fail("empty inventory");
    try {ToolInventoryData.set(original,-1,null);fail("negative slot accepted");} catch (IllegalArgumentException expected) {}
    var duplicate = new ListTag(); duplicate.add(entry(0,"a")); duplicate.add(entry(0,"b"));
    if (ToolInventoryData.set(duplicate,0,entry(0,"c")).size()!=2) fail("duplicate entry lost");
    System.out.println("TCONSTRUCT_TOOL_INVENTORY_OK edits=1 isolation=1 relocation=1 rejection=1");
  }
  private static void fail(String message) {throw new IllegalStateException(message);}
}
