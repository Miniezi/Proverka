"""Second migration pass: lifecycle injection and equivalent NeoForge APIs."""
from pathlib import Path
import re,json

def migrate(root):
 replacements={
  'net.neoforged.neoforge.common.crafting.conditions.':'net.neoforged.neoforge.common.conditions.',
  'ToolActions':'ItemAbilities','ToolAction':'ItemAbility',
  'ForgeFlowingFluid':'BaseFlowingFluid','ForgeBiomeModifiers':'NeoForgeBiomeModifiers',
  'ForgeMod':'NeoForgeMod',
  'mezz.jei.api.forge.':'mezz.jei.api.neoforge.',
  'slimeknights.mantle.registration.deferred.SynchronizedDeferredRegister':'net.neoforged.neoforge.registries.DeferredRegister',
  'SynchronizedDeferredRegister':'DeferredRegister',
  'net.neoforged.neoforge.registries.RegistryObject':'net.neoforged.neoforge.registries.DeferredHolder',
  'net.minecraft.advancements.FrameType':'net.minecraft.advancements.AdvancementType',
  'FrameType':'AdvancementType',
 }
 vanilla={'BLOCKS':'BLOCK','ITEMS':'ITEM','ENTITY_TYPES':'ENTITY_TYPE','FLUIDS':'FLUID','POTIONS':'POTION','FEATURES':'FEATURE','SOUND_EVENTS':'SOUND_EVENT','PARTICLE_TYPES':'PARTICLE_TYPE','RECIPE_SERIALIZERS':'RECIPE_SERIALIZER','BLOCK_ENTITY_TYPES':'BLOCK_ENTITY_TYPE','MOB_EFFECTS':'MOB_EFFECT'}
 counts={};changed=[]
 for f in (root/'src/main/java').rglob('*.java'):
  before=f.read_text();s=before
  for old,new in replacements.items():
   counts[old]=counts.get(old,0)+s.count(old);s=s.replace(old,new)
  s=re.sub(r'\bRegistryObject\s*<','DeferredHolder<?, ',s)
  s=s.replace('import net.neoforged.fml.javafmlmod.FMLJavaModLoadingContext;\n','')
  s=s.replace('FMLJavaModLoadingContext.get().getModEventBus()','slimeknights.tconstruct.TConstruct.getModEventBus()')
  s=s.replace('net.neoforged.neoforge.registries.ForgeRegistries.Keys','net.neoforged.neoforge.registries.NeoForgeRegistries.Keys')
  for old,new in vanilla.items():
   s=s.replace('ForgeRegistries.'+old, 'net.minecraft.core.registries.BuiltInRegistries.'+new)
  s=re.sub(r'\bForgeRegistries\.Keys\.', 'net.neoforged.neoforge.registries.NeoForgeRegistries.Keys.', s)
  # Vanilla registry lookups use get(ResourceLocation), Forge used getValue.
  s=re.sub(r'(BuiltInRegistries\.[A-Z_]+)\.getValue\(',r'\1.get(',s)
  s=s.replace('import net.neoforged.neoforge.registries.ForgeRegistries;\n','') if not re.search(r'\bForgeRegistries\.',s) else s
  if f.name=='TConstruct.java':
   s=s.replace('  public TConstruct() {','''  private static IEventBus modEventBus;

  public static IEventBus getModEventBus() {
    return java.util.Objects.requireNonNull(modEventBus, "TConstruct mod event bus is not initialized");
  }

  public TConstruct(IEventBus bus, net.neoforged.fml.ModContainer modContainer) {
    modEventBus = bus;''')
   s=s.replace('    IEventBus bus = slimeknights.tconstruct.TConstruct.getModEventBus();\n','')
   s=s.replace('Config.init();','Config.init(modContainer);')
   s=s.replace('    TinkerItemDisplays.init();\n','')
   s=s.replace('import net.neoforged.fml.DistExecutor;\n','')
   s=s.replace('DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> TinkerClient::onConstruct);', 'if (net.neoforged.fml.loading.FMLEnvironment.dist == Dist.CLIENT) { TinkerClient.onConstruct(); }')
  if f.name=='Config.java' and 'common/config' in str(f):
   s=s.replace('public static void init() {','public static void init(net.neoforged.fml.ModContainer modContainer) {')
   s=s.replace('ModLoadingContext.get().registerConfig(', 'modContainer.registerConfig(')
   s=s.replace('import net.neoforged.fml.ModLoadingContext;\n','')
  if s!=before:f.write_text(s);changed.append(str(f.relative_to(root)))
 return {'replacements':counts,'changed_files':changed}
