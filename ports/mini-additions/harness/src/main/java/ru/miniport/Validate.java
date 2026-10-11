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
  long functions=java.util.stream.StreamSupport.stream(server.getFunctions().getFunctionNames().spliterator(),false).filter(id->id.getNamespace().equals("inqui")).count();
  if(functions!=69)throw new IllegalStateException("Expected 69 functions, loaded "+functions);
  for(String recipe:new String[]{"ice_sword","ice_bow","mimicry1","mimicry2","mimicry3","ice_nuke","nuke","m_chest","m_feet","m_helmet","m_leegs","cleaner","ice","budd","roasted_tumor"})
   if(server.getRecipeManager().byKey(ResourceLocation.parse("inqui:"+recipe)).isEmpty())throw new IllegalStateException("Missing recipe "+recipe);
  for(String name:new String[]{"root","c_ice_sword","c_ice_bow","c_mimicry1","c_m_chest","a_1","a_2","a_3","a_4"})
   if(server.getAdvancements().get(ResourceLocation.parse("inqui:"+name))==null)throw new IllegalStateException("Missing advancement "+name);
  try(var reader=new java.io.BufferedReader(new java.io.InputStreamReader(getClass().getResourceAsStream("/expected-recipes.txt"),java.nio.charset.StandardCharsets.UTF_8))) {
   int checked=0;
   for(String line:reader.lines().toList()){
    String[] pair=line.split("\\|",2);
    if(net.neoforged.fml.ModList.get().isLoaded(pair[0])){
     if(server.getRecipeManager().byKey(ResourceLocation.parse(pair[1])).isEmpty())throw new IllegalStateException("Port recipe not loaded: "+pair[1]);
     checked++;
    }
   }
   System.out.println("MINI_RECIPES_OK count="+checked);
  }catch(java.io.IOException ex){throw new RuntimeException(ex);}
  var template=server.getStructureManager().get(ResourceLocation.parse("inqui:ff_1")).orElseThrow();
  var saved=template.save(new net.minecraft.nbt.CompoundTag());
  var entityTag=saved.getList("entities",10).getCompound(0).getCompound("nbt");
  var entity=net.minecraft.world.entity.EntityType.loadEntityRecursive(entityTag,server.overworld(),e->e);
  if(!(entity instanceof net.minecraft.world.entity.LivingEntity living) || !living.hasEffect(net.minecraft.world.effect.MobEffects.DAMAGE_RESISTANCE))
   throw new IllegalStateException("Structure guardian lost permanent resistance during migration");
  entity.setPos(0,80,0);server.overworld().addFreshEntity(entity);
  server.getCommands().performPrefixedCommand(server.createCommandSourceStack(),"function inqui:proto_count2");
  server.getCommands().performPrefixedCommand(server.createCommandSourceStack(),"function inqui:proto_count3");
  var raid=server.getScoreboard().getObjective("proto_scamp_raid");
  var spread=server.getScoreboard().getObjective("proto_random_number");
  if(raid==null || spread==null || server.getScoreboard().getPlayerScoreInfo(entity,raid)==null || server.getScoreboard().getPlayerScoreInfo(entity,raid).value()!=884000 || server.getScoreboard().getPlayerScoreInfo(entity,spread)==null || server.getScoreboard().getPlayerScoreInfo(entity,spread).value()!=32)
   throw new IllegalStateException("Proto raid/spread timers did not initialize");
  entity.discard();
  System.out.println("MINI_PROTO_TIMERS_OK");
  System.out.println("MINI_STRUCTURE_ENTITY_OK "+entity.getType());
  System.out.println("MINI_PORT_VALIDATION_OK functions="+functions);
  server.halt(false);
 }
}
