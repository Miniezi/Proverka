package ru.tconstructport;

import net.minecraft.nbt.CompoundTag;
import slimeknights.tconstruct.common.network.SyncPersistentDataPacket;
import net.minecraft.network.FriendlyByteBuf;
import io.netty.buffer.Unpooled;
import slimeknights.tconstruct.library.tools.capability.PersistentDataAttachment;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability;
import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability.TinkerDataKey;
import slimeknights.tconstruct.library.tools.capability.TinkerDataCapability.ComputableDataKey;

final class EntityDataSmoke {
  static void init(IEventBus bus) { TinkerDataCapability.register(bus); PersistentDataAttachment.register(bus); bus.addListener(SyncPersistentDataPacket::register); }
  static void validate(ServerStartedEvent event) {
    var level=event.getServer().overworld();
    var first=EntityType.PIG.create(level);
    var second=EntityType.PIG.create(level);
    if(first==null || second==null) fail("entity construction");
    if(first.hasData(TinkerDataCapability.CAPABILITY)) fail("attachment was not lazy");
    var nonliving=EntityType.ITEM.create(level);
    if(nonliving==null || TinkerDataCapability.findData(nonliving).isPresent() || nonliving.hasData(TinkerDataCapability.CAPABILITY)) fail("nonliving entity received modifier data");
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
    var persistentType=PersistentDataAttachment.TYPE;
    if(first.hasData(persistentType)) fail("persistent data was not lazy");
    var persistent=first.getData(persistentType);
    var nested=new CompoundTag();
    nested.putInt("value",42);
    persistent.put("tconstruct:test",nested);
    var persistentSave=first.saveWithoutId(new CompoundTag());
    var reloaded=EntityType.PIG.create(level);
    if(reloaded==null) fail("persistent reload construction");
    reloaded.load(persistentSave);
    if(reloaded.getData(persistentType).getCompound("tconstruct:test").getInt("value")!=42) fail("persistent save/load");
    reloaded.getData(persistentType).getCompound("tconstruct:test").putInt("value",99);
    if(nested.getInt("value")!=42) fail("reload shared live nested NBT");
    for(boolean death : new boolean[]{true,false}) {
      var clone=EntityType.PIG.create(level);
      if(clone==null) fail("clone construction");
      clone.copyAttachmentsFrom(first,death);
      if(clone.getData(persistentType).getCompound("tconstruct:test").getInt("value")!=42) fail("clone lost persistent data");
      clone.getData(persistentType).getCompound("tconstruct:test").putInt("value",7);
      if(nested.getInt("value")!=42 || clone.hasData(TinkerDataCapability.CAPABILITY)) fail("clone alias or transient copy");
    }
    var empty=EntityType.PIG.create(level);
    var emptyReload=EntityType.PIG.create(level);
    if(empty==null || emptyReload==null) fail("empty construction");
    empty.getData(persistentType);
    emptyReload.load(empty.saveWithoutId(new CompoundTag()));
    if(emptyReload.hasData(persistentType)) fail("empty data unnecessarily serialized");
    var source=new CompoundTag();
    var payloadNested=new CompoundTag();
    payloadNested.putInt("value",123);
    source.put("tconstruct:packet",payloadNested);
    var packet=new SyncPersistentDataPacket(source);
    payloadNested.putInt("value",999);
    var buffer=new FriendlyByteBuf(Unpooled.buffer());
    try {
      SyncPersistentDataPacket.CODEC.encode(buffer,packet);
      var decoded=SyncPersistentDataPacket.CODEC.decode(buffer);
      if(buffer.isReadable() || decoded.data().getCompound("tconstruct:packet").getInt("value")!=123) fail("packet roundtrip or snapshot isolation");
      var target=second.getData(persistentType);
      target.putInt("tconstruct:stale",1);
      decoded.applyTo(target);
      if(target.contains("tconstruct:stale") || target.getCompound("tconstruct:packet").getInt("value")!=123) fail("packet replacement");
      target.getCompound("tconstruct:packet").putInt("value",7);
      if(decoded.data().getCompound("tconstruct:packet").getInt("value")!=123) fail("packet shared target data");
      new SyncPersistentDataPacket(new CompoundTag()).applyTo(target);
      if(!target.isEmpty() || target!=second.getData(persistentType)) fail("empty packet or attachment identity");
    } finally { buffer.release(); }
    System.out.println("TCONSTRUCT_PERSISTENT_PACKET_OK roundtrip=1 snapshot=1 replace=1 empty=1 identity=1");
    System.out.println("TCONSTRUCT_PERSISTENT_DATA_OK save_load=1 death_copy=1 return_copy=1 deep_copy=1 empty_omitted=1");
    System.out.println("TCONSTRUCT_ENTITY_DATA_OK lazy=1 isolated=1 transient=1 computed=1 stable_identity=1");
  }
  private static void fail(String reason) { throw new IllegalStateException(reason); }
}
