package ru.tconstructport;

import net.minecraft.world.item.ItemDisplayContext;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.library.TinkerItemDisplays;

/** Tests migrated enum declarations and cast holder semantics. Never distribute this fixture as TConstruct. */
@Mod("tconstruct")
public final class DisplaySmoke {
  public DisplaySmoke(net.neoforged.bus.api.IEventBus bus) { PotionSmoke.init(bus); EffectSmoke.init(bus); EntityDataSmoke.init(bus); WorldPacketSmoke.init(bus); NetworkSmoke.init(bus); NeoForge.EVENT_BUS.addListener(this::validate); }
  private void validate(ServerStartedEvent event) {
    ItemDisplayContext[] contexts={TinkerItemDisplays.MELTER,TinkerItemDisplays.TABLE,TinkerItemDisplays.CASTING_TABLE,TinkerItemDisplays.CASTING_BASIN,TinkerItemDisplays.FLUID_CANNON,TinkerItemDisplays.THROWN};
    String[] names={"melter","table","casting_table","casting_basin","fluid_cannon","thrown"};
    java.util.Set<Byte> ids=new java.util.HashSet<>();
    for(int i=0;i<contexts.length;i++) {
      var context=contexts[i];
      if(!context.isModded() || !context.getSerializedName().equals("tconstruct:"+names[i]) || !ids.add(context.getId()) || ItemDisplayContext.BY_ID.apply(context.getId())!=context)
        throw new IllegalStateException("Invalid migrated display context: "+names[i]);
      var fallback=(i==2 || i==4 || i==5)?ItemDisplayContext.FIXED:null;
      if(context.fallback()!=fallback) throw new IllegalStateException("Wrong fallback: "+names[i]);
    }
    var name=net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("tconstruct", "fixture");
    var gold=net.minecraft.world.item.Items.GOLD_INGOT;
    var sand=net.minecraft.world.item.Items.SAND;
    var redSand=net.minecraft.world.item.Items.RED_SAND;
    var direct=new slimeknights.tconstruct.common.registration.CastItemObject(name, gold, sand, redSand);
    var holder=net.neoforged.neoforge.registries.DeferredItem.<net.minecraft.world.item.Item>createItem(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(gold));
    var deferred=new slimeknights.tconstruct.common.registration.CastItemObject(name, holder, () -> sand, () -> redSand);
    for(var cast:java.util.List.of(direct, deferred)) {
      if(cast.get()!=gold || cast.asItem()!=gold || cast.getSand()!=sand || cast.getRedSand()!=redSand
        || !cast.values().equals(java.util.List.of(gold,sand,redSand))
        || !cast.id().equals(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(gold))
        || !cast.getSingleUseTag().location().equals(name.withPrefix("casts/single_use/"))
        || !cast.getMultiUseTag().location().equals(name.withPrefix("casts/multi_use/")))
        throw new IllegalStateException("Cast holder migration changed variant identity or tags");
    }
    System.out.println("TCONSTRUCT_CAST_MIGRATION_OK constructors=2 variants=3 tags=2");
    System.out.println("TCONSTRUCT_DISPLAY_MIGRATION_OK contexts=6 unique_ids=6 fallbacks=6");
    PotionSmoke.validate(event);
    EffectSmoke.validate(event);
    RecipeInputSmoke.validate();
    CraftingSmoke.validate(event);
    EntityDataSmoke.validate(event);
    WorldPacketSmoke.validate(event);
    NetworkSmoke.validate(event);
    event.getServer().halt(false);
  }
}
