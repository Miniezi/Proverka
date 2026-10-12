"""Attribute operations, effect modifiers and registry holder migration."""
import re

def migrate(root):
 java=root/'src/main/java'
 for f in java.rglob('*.java'):
  s=f.read_text();old=s
  # Restrict enum renaming to files that actually reference AttributeModifier.
  if 'net.minecraft.world.entity.ai.attributes.AttributeModifier' in s:
   for a,b in [('ADDITION','ADD_VALUE'),('MULTIPLY_BASE','ADD_MULTIPLIED_BASE'),('MULTIPLY_TOTAL','ADD_MULTIPLIED_TOTAL')]:
    s=re.sub(r'\bOperation\.'+a+r'\b','Operation.'+b,s)
  s=s.replace('DeferredHolder<?, Attribute>', 'DeferredHolder<Attribute, Attribute>')
  # LivingEntity query methods now consume holders, not attribute values.
  s=re.sub(r'(getAttribute(?:Value|BaseValue)?\(TinkerAttributes\.\w+)\.get\(\)', r'\1', s)
  if f.name=='TinkerAttributes.java':
   s=re.sub(r'(event.add\(EntityType.PLAYER, \w+)\.get\(\)',r'\1',s)
   s=s.replace('Attributes.KNOCKBACK_RESISTANCE.setSyncable', 'Attributes.KNOCKBACK_RESISTANCE.value().setSyncable')
   s=s.replace('Attribute attr = attribute.get();','net.minecraft.core.Holder<Attribute> attr = attribute;')
  if s!=old:f.write_text(s)
 f=java/'slimeknights/tconstruct/common/TinkerEffect.java';s=f.read_text()
 old='''  public TinkerEffect addAttributeModifier(Attribute pAttribute, String pUuid, double pAmount, Operation pOperation) {
    super.addAttributeModifier(pAttribute, pUuid, pAmount, pOperation);
    return this;
  }'''
 new='''  public TinkerEffect addAttributeModifier(net.minecraft.core.Holder<Attribute> attribute, net.minecraft.resources.ResourceLocation id, double amount, Operation operation) {
    super.addAttributeModifier(attribute, id, amount, operation);
    return this;
  }

  /** Compatibility for existing modifier definitions; retain a stable ID for each legacy UUID. */
  public TinkerEffect addAttributeModifier(Attribute attribute, String uuid, double amount, Operation operation) {
    var registry = net.minecraft.core.registries.BuiltInRegistries.ATTRIBUTE;
    return addAttributeModifier(registry.getHolderOrThrow(registry.getResourceKey(attribute).orElseThrow()), uuid, amount, operation);
  }

  public TinkerEffect addAttributeModifier(net.minecraft.core.Holder<Attribute> attribute, String uuid, double amount, Operation operation) {
    return addAttributeModifier(attribute, net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("tconstruct", "legacy/" + java.util.UUID.fromString(uuid)), amount, operation);
  }

  private static net.minecraft.core.Holder<MobEffect> holder(MobEffect effect) {
    var registry = net.minecraft.core.registries.BuiltInRegistries.MOB_EFFECT;
    return registry.getHolderOrThrow(registry.getResourceKey(effect).orElseThrow());
  }'''
 assert old in s;s=s.replace(old,new)
 s=s.replace('new MobEffectInstance(this,', 'new MobEffectInstance(holder(this),')
 s=s.replace('Supplier<? extends MobEffect> effect', 'net.minecraft.core.Holder<MobEffect> effect')
 s=s.replace('return getAmplifier(entity, effect.get()) + 1;', 'return getAmplifier(entity, effect) + 1;')
 s=s.replace('    MobEffectInstance instance = entity.getEffect(effect);', '''    return getAmplifier(entity, holder(effect));
  }

  public static int getAmplifier(LivingEntity entity, net.minecraft.core.Holder<MobEffect> effect) {
    MobEffectInstance instance = entity.getEffect(effect);''')
 f.write_text(s)
