"""Use the owning level's registries for gameplay ammo persistence.

Context-free inventory hooks and tooltip decoding need explicit lookup propagation later.
"""
def migrate(root):
    folder=root/'src/main/java/slimeknights/tconstruct/library/tools/item/ranged'
    helper='slimeknights.tconstruct.library.tools.nbt.StoredItemStack'
    for name in ['ModifiableBowItem.java','ModifiableCrossbowItem.java']:
        p=folder/name;s=p.read_text()
        s=s.replace('ammo.save(new CompoundTag())',helper+'.write(ammo, level.registryAccess())')
        if name=='ModifiableCrossbowItem.java':
            s=s.replace('ItemStack ammo = ItemStack.of(heldAmmo);', 'ItemStack ammo = '+helper+'.read(heldAmmo, level.registryAccess());')
        p.write_text(s)
    return {'files':2,'context_free_consumers_migrated':False}
