"""Publish completed nested stat and worktable edits, never an unfinished child tag."""

def replace_once(source, old, new):
    assert source.count(old) == 1, (old, source.count(old))
    return source.replace(old, new, 1)


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct'
    p = base / 'tools/modifiers/slotless/StatOverrideModifier.java'
    s = p.read_text()
    s = replace_once(s, '      return data.getCompound(groupKey);',
                     '      return data.getCompound(groupKey).copy();')
    s = replace_once(s, '      data.put(groupKey, nbt);\n      return nbt;', '      return nbt;')
    s = replace_once(s, '      nbt.putFloat(name, value);\n      return true;',
                     '      nbt.putFloat(name, value);\n      tool.getPersistentData().put(groupKey, nbt);\n      return true;')
    s = replace_once(s, '      tool.getPersistentData().remove(groupKey);\n      return false;\n    }\n    return true;',
                     '      tool.getPersistentData().remove(groupKey);\n      return false;\n    }\n    tool.getPersistentData().put(groupKey, nbt);\n    return true;')
    s = replace_once(s, '        nbt.put(name, tag);\n        return true;',
                     '        nbt.put(name, tag);\n        data.put(KEY_BONUS, nbt);\n        return true;')
    s = replace_once(s, '      data.remove(StatOverrideModifier.KEY_BONUS);\n      return false;\n    }\n    return true;',
                     '      data.remove(StatOverrideModifier.KEY_BONUS);\n      return false;\n    }\n    data.put(KEY_BONUS, nbt);\n    return true;')
    s = replace_once(s, '      tool.getPersistentData().remove(StatOverrideModifier.KEY_BONUS);\n      return false;\n    }\n    return true;',
                     '      tool.getPersistentData().remove(StatOverrideModifier.KEY_BONUS);\n      return false;\n    }\n    tool.getPersistentData().put(KEY_BONUS, nbt);\n    return true;')
    p.write_text(s)
    p = base / 'tools/recipe/ToggleInteractionWorktableRecipe.java'
    s = p.read_text()
    for side in ('LEFT', 'RIGHT'):
        s = replace_once(s, f'persistentData.get(InteractionSource.{side}_CLICK.getKey(), LIST_GETTER);',
                         f'persistentData.get(InteractionSource.{side}_CLICK.getKey(), LIST_GETTER).copy();')
    # Publish both lists together: observers must not see a half-completed switch.
    start = s.index('    // if we removed from a list, clear out empty lists')
    end = s.index('    return LazyToolStack.successCopy', start)
    s = s[:start] + '''    if (!removed) {
      StringTag tag = StringTag.valueOf(id.toString());
      if (tool.getHook(ToolHooks.INTERACTION).canInteract(tool, id, InteractionSource.RIGHT_CLICK)) {
        leftList.add(tag);
      } else {
        rightList.add(tag);
      }
    }
    persistentData.edit(data -> {
      String leftKey = InteractionSource.LEFT_CLICK.getKey().toString();
      String rightKey = InteractionSource.RIGHT_CLICK.getKey().toString();
      if (leftList.isEmpty()) data.remove(leftKey);
      else data.put(leftKey, leftList);
      if (rightList.isEmpty()) data.remove(rightKey);
      else data.put(rightKey, rightList);
    });
''' + s[end:]
    p.write_text(s)
    p = base / 'library/recipe/worktable/ModifierSetWorktableRecipe.java'
    s = replace_once(p.read_text(), 'ListTag tagList = persistentData.get(dataKey, LIST_GETTER);',
                     'ListTag tagList = persistentData.get(dataKey, LIST_GETTER).copy();')
    p.write_text(s)
    return {'classes': 3, 'detached_stat_edits': True, 'atomic_interaction_switch': True}
