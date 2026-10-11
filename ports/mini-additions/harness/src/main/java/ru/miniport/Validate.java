package ru.miniport;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.minecraft.resources.ResourceLocation;
@Mod("mini_port_validation")
public class Validate {
 public Validate(){NeoForge.EVENT_BUS.addListener(this::validate);}
 private void validate(ServerStartedEvent event){
  var server=event.getServer();
  long functions=server.getFunctions().getFunctionNames().stream().filter(id->id.getNamespace().equals("inqui")).count();
  if(functions!=69)throw new IllegalStateException("Expected 69 functions, loaded "+functions);
  for(String recipe:new String[]{"ice_sword","ice_bow","mimicry1","mimicry2","mimicry3","ice_nuke","nuke","m_chest","m_feet","m_helmet","m_leegs","cleaner"})
   if(server.getRecipeManager().byKey(ResourceLocation.parse("inqui:"+recipe)).isEmpty())throw new IllegalStateException("Missing recipe "+recipe);
  for(String name:new String[]{"root","c_ice_sword","c_ice_bow","c_mimicry1","c_m_chest","a_1","a_2","a_3","a_4"})
   if(server.getAdvancements().get(ResourceLocation.parse("inqui:"+name))==null)throw new IllegalStateException("Missing advancement "+name);
  System.out.println("MINI_PORT_VALIDATION_OK functions="+functions);
  server.halt(false);
 }
}
