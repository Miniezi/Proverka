"""Make raw-data hook edits explicit and publishable before component owner binding."""
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct'
    p = base / 'library/utils/RestrictedCompoundTag.java'
    s = p.read_text().replace('import lombok.RequiredArgsConstructor;\n', '').replace('@RequiredArgsConstructor\n', '')
    s = replace_once(s, '  private final Set<String> restrictedKeys;', '''  private final Set<String> restrictedKeys;
  @Nullable
  private final java.util.function.Consumer<CompoundTag> publish;

  public RestrictedCompoundTag(CompoundTag tag, Set<String> restrictedKeys) {
    this(tag, restrictedKeys, null);
  }

  public RestrictedCompoundTag(CompoundTag tag, Set<String> restrictedKeys,
                               @Nullable java.util.function.Consumer<CompoundTag> publish) {
    this.tag = tag;
    this.restrictedKeys = Set.copyOf(restrictedKeys);
    this.publish = publish;
  }

  private void changed() {
    if (publish != null) publish.accept(tag.copy());
  }

  /** Edits a detached restricted view and publishes once after successful completion.
   * Nested getter results are snapshots: write edited values back with put(). */
  public void edit(java.util.function.Consumer<RestrictedCompoundTag> edit) {
    CompoundTag snapshot = tag.copy();
    edit.accept(new RestrictedCompoundTag(snapshot, restrictedKeys));
    // Copy again so a retained editor cannot mutate the committed tree later.
    CompoundTag committed = snapshot.copy();
    tag.getAllKeys().clear();
    tag.merge(committed);
    changed();
  }''')
    s = replace_once(s, '    return get(name, CompoundTag::get, null);',
                     '    Tag value = get(name, CompoundTag::get, null);\n    return value == null ? null : value.copy();')
    s = replace_once(s, '    return tag.getCompound(name);', '    return tag.getCompound(name).copy();')
    s = replace_once(s, '    return tag.getList(name, type);', '    return tag.getList(name, type).copy();')
    s = replace_once(s, '      tag.put(name, nbt);', '      tag.put(name, nbt.copy());\n      changed();')
    for call in ['putInt(name, value)', 'putBoolean(name, value)', 'putFloat(name, value)', 'putString(name, value)', 'remove(name)']:
        s = replace_once(s, f'      tag.{call};', f'      tag.{call};\n      changed();')
    p.write_text(s)
    p = base / 'library/tools/nbt/ToolStack.java'
    s = replace_once(p.read_text(), '    this.nbt = tag;\n    clearCache();',
                     '    this.nbt = tag;\n    restrictedNBT = null;\n    clearCache();')
    p.write_text(s)
    return {'classes': 2, 'raw_getters_are_snapshots': True, 'component_owner_bound': False}
