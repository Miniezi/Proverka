package ru.tconstructport;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability;
import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability.TinkerDataKey;
import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability.ComputableDataKey;

final class EntityDataSmoke {
  static void init(IEventBus bus) { TinkerDataCapability.register(bus); }
  static void validate(ServerStartedEvent event) {
    var level=event.getServer().overworld();
    var first=EntityType.PIG.create(level);
    var second=EntityType.PIG.create(level);
    if(first==null || second==null) fail("entity construction");
    if(first.hasData(TinkerDataCapability.CAPABILITY)) fail("attachment was not lazy");
    var data=TinkerDataCapability.getData(first);
    if(!first.hasData(TinkerDataCapability.CAPABILITY) || TinkerDataCapability.findData(first).orElseThrow()!=data) fail("unstable attachment");
    var id=ResourceLocation.fromNamespaceAndPath("tconstruct","fixture_data");
    var key=TinkerDataKey.<Float>of(id);
    var sameName=TinkerDataKey.<Float>of(id);
    data.add(key,2.5f);
    if(data.get(key,0f)!=2.5f || data.contains(sameName) || TinkerDataCapability.getData(second).contains(key)) fail("key or entity isolation");
    data.add(key,-2.5f);
    if(data.contains(key)) fail("zero accumulation retained key");
    var calls=new java.util.concurrent.atomic.AtomicInteger();
    var computed=ComputableDataKey.of(id,()->{calls.incrementAndGet();return new Object();});
    if(data.computeIfAbsent(computed)!=data.computeIfAbsent(computed) || calls.get()!=1) fail("computed key recreated");
    data.remove(computed);
    data.computeIfAbsent(computed);
    if(calls.get()!=2 || !key.id().equals(key.getId())) fail("remove or key ID compatibility");
    data.put(key,7f);
    var saved=first.saveWithoutId(new CompoundTag());
    var restored=EntityType.PIG.create(level);
    if(restored==null) fail("restore construction");
    restored.load(saved);
    if(restored.hasData(TinkerDataCapability.CAPABILITY)) fail("transient attachment restored from save");
    if(TinkerDataCapability.getData(restored).contains(key)) fail("transient data was serialized");
    if(TinkerDataCapability.getData(first)!=data || data.get(key,0f)!=7f) fail("saving changed live attachment");
    System.out.println("TCONSTRUCT_ENTITY_DATA_OK lazy=1 isolated=1 transient=1 computed=1 stable_identity=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
