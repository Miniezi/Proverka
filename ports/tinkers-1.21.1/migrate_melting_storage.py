"""Carry dynamic registry context from controllers to melting inventory item codecs."""
from migrate_nested_modifier_edits import replace_once


def migrate(root):
    base = root / 'src/main/java/slimeknights/tconstruct/smeltery/block/entity'
    provider = 'net.minecraft.core.HolderLookup.Provider registries'
    for name in ['MeltingModule', 'MeltingModuleInventory']:
        p = base / f'module/{name}.java'
        s = replace_once(p.read_text(), 'public CompoundTag writeToTag()', f'public CompoundTag writeToTag({provider})')
        s = replace_once(s, 'public void readFromTag(CompoundTag nbt)', f'public void readFromTag(CompoundTag nbt, {provider})')
        if name == 'MeltingModule':
            s = replace_once(s, '      stack.save(nbt);',
                             '      nbt = slimeknights.tconstruct.library.tools.nbt.StoredItemStack.write(stack, registries);')
            s = replace_once(s, '    stack = ItemStack.of(nbt);',
                             '    stack = slimeknights.tconstruct.library.tools.nbt.StoredItemStack.read(nbt, registries);')
            s = replace_once(s, '      requiredTemp = nbt.getInt(TAG_REQUIRED_TEMP);\n    }',
                             '      requiredTemp = nbt.getInt(TAG_REQUIRED_TEMP);\n    } else {\n      currentTime = 0;\n      requiredTime = 0;\n      requiredTemp = 0;\n    }')
        else:
            s = replace_once(s, 'modules[i].writeToTag()', 'modules[i].writeToTag(registries)')
            s = replace_once(s, 'getModule(slot).readFromTag(item)', 'getModule(slot).readFromTag(item, registries)')
        p.write_text(s)
    for name, tag in [('MelterBlockEntity', 'tag'), ('HeatingStructureBlockEntity', 'nbt')]:
        p = base / f'controller/{name}.java'
        s = replace_once(p.read_text(), f'meltingInventory.readFromTag({tag}.getCompound(TAG_INVENTORY))',
                         f'meltingInventory.readFromTag({tag}.getCompound(TAG_INVENTORY), registries)')
        s = replace_once(s, 'meltingInventory.writeToTag()', 'meltingInventory.writeToTag(registries)')
        if name == 'MelterBlockEntity':
            s = replace_once(s, 'tank.readFromNBT(tag.getCompound(NBTTags.TANK))',
                             'tank.readFromNBT(registries, tag.getCompound(NBTTags.TANK))')
            s = replace_once(s, 'tank.writeToNBT(new CompoundTag())', 'tank.writeToNBT(registries, new CompoundTag())')
        p.write_text(s)
    return {'classes': 4, 'melting_inventory_registry_chain': True, 'melter_tank_registry_io': True}
