"""Publish nested inventory mutations only after successful detached edits."""
def migrate(root):
    p=root/'src/main/java/slimeknights/tconstruct/library/tools/capability/inventory/InventoryModule.java'
    s=p.read_text()
    start=s.index('  @Override\n  public void setStack(')
    end=s.index('  /* Validation */', start)
    s=s[:start]+'''  @Override
  public void setStack(IToolStackView tool, ModifierEntry modifier, int slot, ItemStack stack) {
    if (slot < 0 || slot >= getSlots(tool, modifier)) return;
    ModDataNBT modData = tool.getPersistentData();
    ResourceLocation key = getKey(modifier.getModifier());
    ListTag current = modData.get(key, GET_COMPOUND_LIST);
    CompoundTag replacement = stack.isEmpty() ? null : writeStack(stack, slot, new CompoundTag());
    ListTag updated = slimeknights.tconstruct.library.tools.nbt.ToolInventoryData.set(current, slot, replacement);
    if (!updated.equals(current)) {
      if (updated.isEmpty()) modData.remove(key);
      else modData.put(key, updated);
    }
  }

'''+s[end:]
    start=s.index('  @Nullable\n  @Override\n  public Component validate(')
    end=s.index('  @Nullable\n  @Override\n  public Component onRemoved(',start)
    s=s[:start]+'''  @Nullable
  @Override
  public Component validate(IToolStackView tool, ModifierEntry modifier) {
    if (condition.tool().matches(tool) && validationLevel.test(modifier.getLevel())) {
      ModDataNBT data = tool.getPersistentData();
      ResourceLocation key = getKey(modifier.getModifier());
      ListTag current = data.get(key, GET_COMPOUND_LIST);
      var fitted = slimeknights.tconstruct.library.tools.nbt.ToolInventoryData.fit(current, getSlots(tool, modifier));
      if (fitted.isEmpty()) return HAS_ITEMS;
      if (!fitted.get().equals(current)) data.put(key, fitted.get());
    }
    return null;
  }

'''+s[end:]
    s=s.replace('if (slot < getSlots(tool, modifier) &&', 'if (slot >= 0 && slot < getSlots(tool, modifier) &&')
    s=s.replace('if (slot < max) {','if (slot >= 0 && slot < max) {')
    p.write_text(s)
    return {'files':1, 'item_serialization_migrated':False}
