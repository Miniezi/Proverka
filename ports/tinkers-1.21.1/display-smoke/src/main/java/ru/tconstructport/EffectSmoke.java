package ru.tconstructport;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.AttributeModifier.Operation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import slimeknights.tconstruct.common.TinkerEffect;

final class EffectSmoke {
  private static final DeferredRegister<MobEffect> REGISTER = DeferredRegister.create(Registries.MOB_EFFECT, "tconstruct");
  private static final DeferredHolder<MobEffect,TinkerEffect> ADD = REGISTER.register("fixture_add", () ->
    new TinkerEffect(MobEffectCategory.BENEFICIAL, true).addAttributeModifier(Attributes.MAX_HEALTH,
      ResourceLocation.fromNamespaceAndPath("tconstruct", "fixture_health"), 4, Operation.ADD_VALUE));
  private static final DeferredHolder<MobEffect,TinkerEffect> SCALE = REGISTER.register("fixture_scale", () ->
    new TinkerEffect(MobEffectCategory.BENEFICIAL, false).addAttributeModifier(Attributes.MAX_HEALTH.value(),
      "ccffb654-9988-451e-9539-f74934274df1", 0.25, Operation.ADD_MULTIPLIED_BASE));

  static void init(IEventBus bus) { REGISTER.register(bus); }
  static void validate(ServerStartedEvent event) {
    var entity = EntityType.PIG.create(event.getServer().overworld());
    if (entity == null) throw new IllegalStateException("No test entity");
    double base = entity.getAttributeValue(Attributes.MAX_HEALTH);
    var added = ADD.get().apply(entity, 200, 1, false);
    if (added.getDuration()!=200 || added.getAmplifier()!=1 || added.showIcon()
      || TinkerEffect.getLevel(entity, ADD)!=2 || TinkerEffect.getAmplifier(entity, ADD)!=1)
      throw new IllegalStateException("Effect level, duration or visibility changed");
    check(entity.getAttributeValue(Attributes.MAX_HEALTH), base + 8);
    entity.removeEffect(ADD);
    check(entity.getAttributeValue(Attributes.MAX_HEALTH), base);
    if(TinkerEffect.getLevel(entity, ADD)!=0 || TinkerEffect.getAmplifier(entity, ADD)!=-1)
      throw new IllegalStateException("Removed effect remains active");
    SCALE.get().apply(entity, 100, 1);
    check(entity.getAttributeValue(Attributes.MAX_HEALTH), base * 1.5);
    // Reapplying must update the same modifier instead of stacking another copy.
    SCALE.get().apply(entity, 150, 1);
    check(entity.getAttributeValue(Attributes.MAX_HEALTH), base * 1.5);
    entity.removeEffect(SCALE);
    check(entity.getAttributeValue(Attributes.MAX_HEALTH), base);
    System.out.println("TCONSTRUCT_EFFECT_MIGRATION_OK operations=2 removal=2 no_duplicate_modifiers=1");
  }
  private static void check(double actual, double expected) {
    if(Math.abs(actual-expected)>0.00001) throw new IllegalStateException("Attribute mismatch: " + actual + " != " + expected);
  }
}
