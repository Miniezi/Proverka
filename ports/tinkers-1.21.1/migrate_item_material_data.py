"""Move material part/list stack storage to immutable vanilla custom-data components.

ToolStack's mutable view and vanilla damage/name data require a separate migration.
Do not mechanically replace its getTag calls with detached snapshots.
"""
def migrate(root):
    source = root/'src/main/java/slimeknights/tconstruct'
    helper = 'slimeknights.tconstruct.library.tools.nbt.ItemStackData'
    paths = ['library/tools/part/IMaterialItem.java',
             'library/tools/part/MaterialItem.java',
             'library/tools/part/block/MaterialBlockItem.java',
             'library/tools/nbt/MaterialIdNBT.java']
    for name in paths:
        p = source/name
        s = p.read_text()
        s = s.replace('stack.getTag()', helper+'.read(stack)')
        s = s.replace('stack.getOrCreateTag().putString(MATERIAL_TAG, material.toString());',
                      helper+'.update(stack, data -> data.putString(MATERIAL_TAG, material.toString()));')
        s = s.replace('stack.getOrCreateTag().put(ToolStack.TAG_MATERIALS, serializeToNBT());',
                      helper+'.update(stack, data -> data.put(ToolStack.TAG_MATERIALS, serializeToNBT()));')
        if name.endswith('MaterialIdNBT.java'):
            s = s.replace('if (index < list.size()) {', 'if (index >= 0 && index < list.size()) {')
        p.write_text(s)
    return {'files': len(paths), 'storage': 'minecraft:custom_data', 'tool_stack_migrated': False}
