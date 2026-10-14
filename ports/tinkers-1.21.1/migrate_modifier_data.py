"""Add explicit publication to mutable modifier data before ToolStack component binding."""
def migrate(root):
    folder=root/'src/main/java/slimeknights/tconstruct/library/tools/nbt'
    p=folder/'ModDataNBT.java';s=p.read_text()
    s=s.replace('@AllArgsConstructor(access = AccessLevel.PROTECTED)\n','')
    marker='  private final CompoundTag data;'
    s=s.replace(marker,marker+'''
  @EqualsAndHashCode.Exclude
  private final ModifierDataStorage storage;

  protected ModDataNBT(CompoundTag data) {
    this(data, null);
  }

  protected ModDataNBT(CompoundTag data, java.util.function.Consumer<CompoundTag> publish) {
    this.data = data;
    this.storage = new ModifierDataStorage(data, publish);
  }

  /** Notify the component owner after a completed mutation. */
  protected void changed() { storage.changed(); }

  /** Explicit transaction for compound/list edits; do not mutate getter results in new code. */
  public void edit(java.util.function.Consumer<CompoundTag> edit) { storage.edit(edit); }
''')
    for line in ['data.put(name.toString(), nbt);','data.putInt(name.toString(), value);',
                 'data.putBoolean(name.toString(), value);','data.putFloat(name.toString(), value);',
                 'data.putString(name.toString(), value);','data.remove(name.toString());']:
        s=s.replace(line,line+'\n    changed();')
    s=s.replace('    this.data.getAllKeys().clear();\n    this.data.merge(data);','    storage.replace(data);')
    s=s.replace('  public static ModDataNBT readFromNBT(CompoundTag data) {','''  /** Working data is shared; published snapshots are detached. */
  public static ModDataNBT readFromNBT(CompoundTag data, java.util.function.Consumer<CompoundTag> publish) {
    return new ModDataNBT(data, publish);
  }

  public static ModDataNBT readFromNBT(CompoundTag data) {''')
    p.write_text(s)
    p=folder/'ToolDataNBT.java';s=p.read_text()
    s=s.replace('  @Override\n  public int getSlots', '''  protected ToolDataNBT(CompoundTag nbt, java.util.function.Consumer<CompoundTag> publish) {
    super(nbt, publish);
  }

  @Override
  public int getSlots''')
    s=s.replace('      getData().putInt(type.getName(), value);\n    }','      getData().putInt(type.getName(), value);\n    }\n    changed();')
    s=s.replace('  public static ToolDataNBT readFromNBT(CompoundTag data) {','''  public static ToolDataNBT readFromNBT(CompoundTag data, java.util.function.Consumer<CompoundTag> publish) {
    return new ToolDataNBT(data, publish);
  }

  public static ToolDataNBT readFromNBT(CompoundTag data) {''')
    p.write_text(s)
    p=root/'src/main/java/slimeknights/tconstruct/library/recipe/worktable/ModifierSetWorktableRecipe.java'
    s=p.read_text().replace('      persistentData.remove(dataKey);\n    }',
                           '      persistentData.remove(dataKey);\n    } else if (!addToSet) {\n      persistentData.put(dataKey, tagList);\n    }')
    p.write_text(s)
    return {'classes':3, 'component_owner_bound':False}
