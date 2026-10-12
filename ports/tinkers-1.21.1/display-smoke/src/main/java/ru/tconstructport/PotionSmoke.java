package ru.tconstructport;

import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionBrewing;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.brewing.RegisterBrewingRecipesEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.mantle.registration.deferred.PotionDeferredRegister;
import slimeknights.mantle.registration.deferred.PotionDeferredRegister.PotionType;
import slimeknights.tconstruct.common.registration.TinkerBrewing;

/** Isolated migration test, not a playable TConstruct build. */
final class PotionSmoke {
  private static final PotionDeferredRegister REGISTER = new PotionDeferredRegister("tconstruct");
  private static final slimeknights.mantle.registration.object.EnumObject<PotionType,Potion> ALL =
    REGISTER.registerTypes("fixture_all", MobEffects.LEVITATION, 300, 0).withStrong().withLong(800, 0).build();
  private static final slimeknights.mantle.registration.object.EnumObject<PotionType,Potion> LIMITED =
    REGISTER.registerTypes("fixture_limited", MobEffects.LEVITATION, 1800, 0).withLong().build();

  static void init(IEventBus bus) {
    REGISTER.register(bus);
    NeoForge.EVENT_BUS.addListener(PotionSmoke::register);
  }
  private static void register(RegisterBrewingRecipesEvent event) {
    TinkerBrewing.register(event.getBuilder(), ALL, Potions.AWKWARD, Items.SLIME_BALL);
    TinkerBrewing.register(event.getBuilder(), LIMITED, Potions.AWKWARD, Items.ENDER_PEARL);
  }
  static void validate(ServerStartedEvent event) {
    checkEffect(ALL.getHolder(PotionType.NORMAL), 300, 0);
    checkEffect(ALL.getHolder(PotionType.STRONG), 150, 1);
    checkEffect(ALL.getHolder(PotionType.LONG), 800, 0);
    checkEffect(LIMITED.getHolder(PotionType.NORMAL), 1800, 0);
    checkEffect(LIMITED.getHolder(PotionType.LONG), 4800, 0);
    if (LIMITED.getHolder(PotionType.STRONG) != null) throw new IllegalStateException("Unexpected strong variant");
    // Rebuilding twice catches accidental registration into a global/static mix list.
    for (int rebuild=0; rebuild<2; rebuild++) {
      var brewing = PotionBrewing.bootstrap(FeatureFlags.DEFAULT_FLAGS, event.getServer().registryAccess());
      for (var container : java.util.List.of(Items.POTION, Items.SPLASH_POTION, Items.LINGERING_POTION)) {
        checkMix(brewing, container, Potions.AWKWARD, Items.SLIME_BALL, ALL.getHolder(PotionType.NORMAL));
        checkMix(brewing, container, ALL.getHolder(PotionType.NORMAL), Items.REDSTONE, ALL.getHolder(PotionType.LONG));
        checkMix(brewing, container, ALL.getHolder(PotionType.NORMAL), Items.GLOWSTONE_DUST, ALL.getHolder(PotionType.STRONG));
        checkMix(brewing, container, Potions.AWKWARD, Items.ENDER_PEARL, LIMITED.getHolder(PotionType.NORMAL));
        checkMix(brewing, container, LIMITED.getHolder(PotionType.NORMAL), Items.REDSTONE, LIMITED.getHolder(PotionType.LONG));
        var noStrong = bottle(container, LIMITED.getHolder(PotionType.NORMAL));
        if (brewing.hasMix(noStrong, new ItemStack(Items.GLOWSTONE_DUST))) throw new IllegalStateException("Created absent strong recipe");
        if (brewing.hasMix(noStrong, new ItemStack(Items.DIRT))) throw new IllegalStateException("Accepted wrong ingredient");
      }
    }
    System.out.println("TCONSTRUCT_POTION_MIGRATION_OK effects=5 containers=3 rebuilds=2 mixes=30");
  }
  private static ItemStack bottle(net.minecraft.world.item.Item item, Holder<Potion> potion) {
    var stack = new ItemStack(item);
    stack.set(DataComponents.POTION_CONTENTS, new PotionContents(potion));
    return stack;
  }
  private static void checkEffect(Holder<Potion> potion, int duration, int amplifier) {
    var effects = potion.value().getEffects();
    if(effects.size()!=1 || !effects.getFirst().getEffect().equals(MobEffects.LEVITATION)
      || effects.getFirst().getDuration()!=duration || effects.getFirst().getAmplifier()!=amplifier)
      throw new IllegalStateException("Changed potion duration, amplifier or effect");
  }
  private static void checkMix(PotionBrewing brewing, net.minecraft.world.item.Item container,
                               Holder<Potion> from, net.minecraft.world.item.Item ingredient, Holder<Potion> to) {
    var input = bottle(container, from);
    var reagent = new ItemStack(ingredient);
    var output = brewing.mix(reagent, input);
    if(!brewing.hasMix(input,reagent) || !output.is(container)
      || !output.getOrDefault(DataComponents.POTION_CONTENTS, PotionContents.EMPTY).potion().orElseThrow().equals(to)
      || !input.get(DataComponents.POTION_CONTENTS).potion().orElseThrow().equals(from))
      throw new IllegalStateException("Brewing lost its container, changed input or produced wrong potion");
  }
}
