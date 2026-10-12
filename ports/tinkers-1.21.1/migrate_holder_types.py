"""Resolve NeoForge holder registry base types without erasing generic safety."""
import re

BASES={
 'CreativeModeTab':'net.minecraft.world.item.CreativeModeTab',
 'SimpleParticleType':'net.minecraft.core.particles.ParticleType<?>',
 'ParticleType':'net.minecraft.core.particles.ParticleType<?>',
 'EntityDataSerializer':'net.minecraft.network.syncher.EntityDataSerializer<?>',
 'BlockEntityType':'net.minecraft.world.level.block.entity.BlockEntityType<?>',
 'EntityType':'net.minecraft.world.entity.EntityType<?>',
 'MenuType':'net.minecraft.world.inventory.MenuType<?>',
 'RecipeType':'net.minecraft.world.item.crafting.RecipeType<?>',
 'RecipeSerializer':'net.minecraft.world.item.crafting.RecipeSerializer<?>',
 'TypeAwareRecipeSerializer':'net.minecraft.world.item.crafting.RecipeSerializer<?>',
 'SimpleRecipeSerializer':'net.minecraft.world.item.crafting.RecipeSerializer<?>',
 'LootItemConditionType':'net.minecraft.world.level.storage.loot.predicates.LootItemConditionType',
 'LootItemFunctionType':'net.minecraft.world.level.storage.loot.functions.LootItemFunctionType<?>',
 'LootPoolEntryType':'net.minecraft.world.level.storage.loot.entries.LootPoolEntryType',
 'StructurePieceType':'net.minecraft.world.level.levelgen.structure.pieces.StructurePieceType',
 'StructureType':'net.minecraft.world.level.levelgen.structure.StructureType<?>',
 'TreeDecoratorType':'net.minecraft.world.level.levelgen.feature.treedecorators.TreeDecoratorType<?>',
 'RootPlacerType':'net.minecraft.world.level.levelgen.feature.rootplacers.RootPlacerType<?>',
 'SlimeTreeFeature':'net.minecraft.world.level.levelgen.feature.Feature<?>',
 'SlimeFungusFeature':'net.minecraft.world.level.levelgen.feature.Feature<?>',
 'Block':'net.minecraft.world.level.block.Block',
 'GlowBlock':'net.minecraft.world.level.block.Block',
 'Item':'net.minecraft.world.item.Item',
 'Potion':'net.minecraft.world.item.alchemy.Potion',
 'MobEffect':'net.minecraft.world.effect.MobEffect',
}
for effect in ('TinkerEffect','BleedingEffect','MagneticEffect','RepulsiveEffect','AntigravityEffect','ReturningEffect','CarryPotionEffect','HelmetChargingEffect'):
 BASES[effect]='net.minecraft.world.effect.MobEffect'

def migrate(root):
 changed=0;unknown=set()
 for f in (root/'src/main/java').rglob('*.java'):
  s=f.read_text();edits=[]
  for m in re.finditer(r'\bDeferredHolder<\?,\s*',s):
   start=m.end();end=start;depth=0
   while end<len(s):
    if s[end]=='<':depth+=1
    elif s[end]=='>':
     if depth==0:break
     depth-=1
    end+=1
   value=s[start:end].strip()
   outer=re.sub(r'^\? extends\s+','',value).split('<',1)[0]
   base=BASES.get(outer)
   if base:edits.append((m.start(),start,'DeferredHolder<'+base+', '))
   else:unknown.add(value)
  for start,end,new in reversed(edits):s=s[:start]+new+s[end:]
  if edits:f.write_text(s);changed+=len(edits)
 return {'converted':changed,'unresolved':sorted(unknown)}
