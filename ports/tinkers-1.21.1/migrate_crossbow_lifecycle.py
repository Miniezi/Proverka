"""Complete native crossbow attribution, contextual ammo tooltip and charge signatures."""
import shutil

def migrate(root):
    folder=root/'src/main/java/slimeknights/tconstruct/library/tools/item/ranged'
    for name in ['ModifiableLauncherItem.java','ModifiableBowItem.java','ModifiableCrossbowItem.java']:
        p=folder/name;s=p.read_text()
        s=s.replace('getUseDuration(ItemStack pStack)', 'getUseDuration(ItemStack pStack, LivingEntity living)')
        s=s.replace('getUseDuration(stack)', 'getUseDuration(stack, living)')
        s=s.replace('getUseDuration(bow)', 'getUseDuration(bow, living)')
        if name=='ModifiableCrossbowItem.java':
            s=s.replace('          arrow.setShotFromCrossbow(true);\n','')
            s=s.replace('      ItemStack heldStack = ItemStack.of(heldAmmo);', '''      net.minecraft.core.HolderLookup.Provider registries = player != null
        ? player.level().registryAccess() : slimeknights.mantle.client.SafeClientAccess.getRegistryAccess();
      // Outside a world no dynamic registry exists; retain the stored data until a lookup is available.
      ItemStack heldStack = registries == null ? ItemStack.EMPTY
        : slimeknights.tconstruct.library.tools.nbt.StoredItemStack.read(heldAmmo, registries);''')
        p.write_text(s)
    meta=root/'src/main/resources/META-INF/mods.toml'
    meta.write_text(meta.read_text()+'\n[[mixins]]\nconfig="tconstruct-port.mixins.json"\n')
    old=root/'src/generated/resources/data/tconstruct/tags/items/modifiable/ranged/crossbows.json'
    new=root/'src/generated/resources/data/tconstruct/tags/item/modifiable/ranged/crossbows.json'
    new.parent.mkdir(parents=True,exist_ok=True);shutil.move(old,new)
    return {'classes':3,'crossbow_tag_resources':1,'native_attribution':'weapon tag mixin'}
