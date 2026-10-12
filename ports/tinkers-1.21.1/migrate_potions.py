"""Port potion registration and brewing to holder-based, per-level builders."""
import re

def migrate(root):
 p=root/'src/main/java/slimeknights/tconstruct'
 f=p/'common/registration/PotionDeferredRegister.java'
 s=f.read_text().replace('DeferredRegisterWrapper', 'EnumDeferredRegister')
 s=re.sub(r'  /\*\* Registers a standalone potion \*/.*?\n  }\n', '', s, flags=re.S)
 s=s.replace('Supplier<? extends MobEffect>', 'net.minecraft.core.Holder<MobEffect>')
 s=s.replace('DeferredHolder<?, ? extends MobEffect>', 'DeferredHolder<MobEffect, ? extends MobEffect>')
 s=s.replace('new MobEffectInstance(effect.get(),', 'new MobEffectInstance(effect,')
 s=s.replace('modID + "."', 'getNamespace() + "."')
 f.write_text(s)
 f=p/'shared/TinkerEffects.java';s=f.read_text()
 s=re.sub(r'DeferredHolder<\?, (\w+)>', r'DeferredHolder<net.minecraft.world.effect.MobEffect, \1>',s)
 s=s.replace('() -> MobEffects.LEVITATION', 'MobEffects.LEVITATION')
 s=s.replace('living.hasEffect(enderference.get())', 'living.hasEffect(enderference)')
 s=s.replace('    POTIONS.register(', '    net.neoforged.neoforge.common.NeoForge.EVENT_BUS.addListener(TinkerEffects::registerBrewing);\n    POTIONS.register(')
 start=s.index('  @SubscribeEvent\n  void commonSetup(')
 end=s.index('  /** Checks if the given entity', start)
 s=s[:start]+'''  private static void registerBrewing(net.neoforged.neoforge.event.brewing.RegisterBrewingRecipesEvent event) {
    var builder = event.getBuilder();
    slimeknights.tconstruct.common.registration.TinkerBrewing.register(builder, experiencedPotion, Potions.AWKWARD, TinkerWorld.congealedSlime.get(SlimeType.EARTH).asItem());
    slimeknights.tconstruct.common.registration.TinkerBrewing.register(builder, ricochetPotion, Potions.AWKWARD, TinkerWorld.congealedSlime.get(SlimeType.SKY).asItem());
    slimeknights.tconstruct.common.registration.TinkerBrewing.register(builder, levitationPotion, Potions.AWKWARD, TinkerWorld.congealedSlime.get(SlimeType.ICHOR).asItem());
    slimeknights.tconstruct.common.registration.TinkerBrewing.register(builder, enderferencePotion, Potions.AWKWARD, TinkerWorld.congealedSlime.get(SlimeType.ENDER).asItem());
  }

'''+s[end:]
 f.write_text(s)
