package ru.tconstructport;

import net.minecraft.world.item.ItemDisplayContext;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import slimeknights.tconstruct.library.TinkerItemDisplays;

/** Tests the migrated enum declarations only. Never distribute this fixture as TConstruct. */
@Mod("tconstruct")
public final class DisplaySmoke {
  public DisplaySmoke() { NeoForge.EVENT_BUS.addListener(this::validate); }
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
    System.out.println("TCONSTRUCT_DISPLAY_MIGRATION_OK contexts=6 unique_ids=6 fallbacks=6");
    event.getServer().halt(false);
  }
}
