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
        if name.endswith('IMaterialItem.java'):
            s = s.replace('  MaterialVariantId getMaterial(ItemStack stack);', '''  MaterialVariantId getMaterial(ItemStack stack);

  /** Base rarity derived from material; items may opt out independently of vanilla components. */
  default net.minecraft.world.item.Rarity getMaterialRarity(ItemStack stack) {
    return MaterialRegistry.getMaterial(getMaterial(stack).getId()).getRarity();
  }''')
            s = s.replace('    return stack;\n  }\n\n  /** Returns the item with the given material',
                          '    MaterialItem.refreshMaterial(stack);\n    return stack;\n  }\n\n  /** Returns the item with the given material', 1)
        if name.endswith('MaterialItem.java') and not name.endswith('IMaterialItem.java'):
            s = s.replace('  @Override\n  public Rarity getRarity(ItemStack stack) {\n    return MaterialRegistry.getMaterial(getMaterial(stack).getId()).getRarity();\n  }\n', '')
            s = s.replace('@Nullable Level worldIn', 'TooltipContext context')
            s = s.replace('  public void verifyTagAfterLoad(CompoundTag nbt) {\n    verifyTag(nbt);\n  }', '''  public void verifyComponentsAfterLoad(ItemStack stack) {
    refreshMaterial(stack);
  }

  /** Refresh redirects and derived rarity only after the material registry is ready. */
  public static void refreshMaterial(ItemStack stack) {
    if (stack.isEmpty() || !MaterialRegistry.isFullyLoaded() || !(stack.getItem() instanceof IMaterialItem)) return;
    CompoundTag data = slimeknights.tconstruct.library.tools.nbt.ItemStackData.read(stack);
    MaterialVariantId before = getMaterialId(data);
    verifyTag(data);
    MaterialVariantId after = getMaterialId(data);
    if (!after.equals(before)) {
      slimeknights.tconstruct.library.tools.nbt.ItemStackData.update(stack,
        current -> current.putString(IMaterialItem.MATERIAL_TAG, after.toString()));
    }
    Rarity rarity = ((IMaterialItem)stack.getItem()).getMaterialRarity(stack);
    if (stack.get(net.minecraft.core.component.DataComponents.RARITY) != rarity) {
      stack.set(net.minecraft.core.component.DataComponents.RARITY, rarity);
    }
  }

  @Override
  public void inventoryTick(ItemStack stack, Level level, net.minecraft.world.entity.Entity entity, int slot, boolean selected) {
    super.inventoryTick(stack, level, entity, slot, selected);
    if (!level.isClientSide) refreshMaterial(stack);
  }''')
        if name.endswith('MaterialBlockItem.java'):
            s = s.replace('  @Override\n  public Rarity getRarity(ItemStack stack) {\n    return MaterialRegistry.getMaterial(getMaterial(stack).getId()).getRarity();\n  }\n', '')
            s = s.replace('@Nullable Level level, List<Component> tooltip', 'TooltipContext context, List<Component> tooltip')
            s = s.replace('super.appendHoverText(stack, level, tooltip, flag);', 'super.appendHoverText(stack, context, tooltip, flag);')
            s = s.replace('  public void verifyTagAfterLoad(CompoundTag tag) {\n    MaterialItem.verifyTag(tag);\n  }', '''  public void verifyComponentsAfterLoad(ItemStack stack) {
    MaterialItem.refreshMaterial(stack);
  }

  @Override
  public void inventoryTick(ItemStack stack, Level level, net.minecraft.world.entity.Entity entity, int slot, boolean selected) {
    super.inventoryTick(stack, level, entity, slot, selected);
    if (!level.isClientSide) MaterialItem.refreshMaterial(stack);
  }''')
        p.write_text(s)
    subclasses = ['tools/item/FakeStorageBlockItem.java', 'tools/item/FakeIngotItem.java',
                  'tools/item/RepairKitItem.java', 'library/tools/part/ToolPartItem.java',
                  'library/tools/part/block/ToolPartBlockItem.java', 'tables/item/AnvilBlockItem.java']
    for name in subclasses:
        p = source/name
        s = p.read_text().replace('public Rarity getRarity(ItemStack stack)', 'public Rarity getMaterialRarity(ItemStack stack)')
        # These tooltip overrides do not otherwise use the former nullable world parameter.
        import re
        s = re.sub(r'public void appendHoverText\(ItemStack stack, @Nullable Level (?:world|level|worldIn),',
                   'public void appendHoverText(ItemStack stack, TooltipContext context,', s)
        s = re.sub(r'appendHoverText\(stack, (?:world|level|worldIn), tooltip, flag\)',
                   'appendHoverText(stack, context, tooltip, flag)', s)
        p.write_text(s)
    return {'files': len(paths) + len(subclasses), 'storage': 'minecraft:custom_data', 'tool_stack_migrated': False}
