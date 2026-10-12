"""Port single-entry holders to NeoForge; retain Mantle multi-form wrappers."""
import re

def migrate(root):
 count=0
 for f in (root/'src/main/java').rglob('*.java'):
  s=f.read_text();before=s
  if f.name == 'TinkerItemModelProvider.java':
   s=s.replace('cast.getId()', 'cast.id()')
  if 'import slimeknights.mantle.registration.object.ItemObject;' not in s:
   continue
  if f.name in ('CastItemObject.java','GeodeItemObject.java'):
   s=s.replace('extends ItemObject<Item>', 'extends ItemObject<Item, Item>')
   s=s.replace('ItemObject<? extends Item> gold', 'net.neoforged.neoforge.registries.DeferredItem<? extends Item> gold')
   s=s.replace('super(gold);', 'super(gold.getKey(), gold);')
   s=s.replace('super(BuiltInRegistries.ITEM, gold);', 'super(getHolder(BuiltInRegistries.ITEM, gold));')
   s=s.replace('= getHolder(BuiltInRegistries.ITEM, sand);', '= getHolder(BuiltInRegistries.ITEM, sand)::value;')
   s=s.replace('= getHolder(BuiltInRegistries.ITEM, redSand);', '= getHolder(BuiltInRegistries.ITEM, redSand)::value;')
   s=s.replace('DeferredHolder<?, ? extends Item> shard', 'DeferredHolder<Item, ? extends Item> shard')
   s=s.replace('super(shard);', 'super(shard.getKey(), shard);')
  else:
   s=s.replace('new ItemObject<>(RegistryObject.create(getResource("minotaur_axe"), net.minecraft.core.registries.BuiltInRegistries.ITEM))', 'net.neoforged.neoforge.registries.DeferredItem.createItem(getResource("minotaur_axe"))')
   s=s.replace('Consumer<ItemObject<?>>', 'Consumer<net.minecraft.world.level.ItemLike>')
   if f.name=='AdvancementsProvider.java':
    s=s.replace('item.getId().getPath(), hasItem(item)', 'net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(item.asItem()).getPath(), hasItem(item)')
   def replace(m):
    t=m.group(1)
    if t.endswith('Block'):
     return 'net.neoforged.neoforge.registries.DeferredBlock<'+t+'>'
    if t.endswith('Item'):
     return 'net.neoforged.neoforge.registries.DeferredItem<'+t+'>'
    raise ValueError(f'Unclassified holder {t} in {f}')
   s=re.sub(r'\bItemObject<([^<>]+)>',replace,s)
   s=s.replace('import slimeknights.mantle.registration.object.ItemObject;\n','')
  if s!=before:f.write_text(s);count+=1
 return count
