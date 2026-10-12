"""Preserve pre/post and logical-client filtering with NeoForge split tick events."""
def migrate(root):
 p=root/'src/main/java/slimeknights/tconstruct/tools'
 for relative,phase in [('ToolClientEvents.java','Pre'),('logic/EquipmentChangeWatcher.java','Post')]:
  f=p/relative;s=f.read_text()
  s=s.replace('import net.neoforged.neoforge.event.TickEvent.Phase;\n','')
  s=s.replace('import net.neoforged.neoforge.event.TickEvent.PlayerTickEvent;', 'import net.neoforged.neoforge.event.tick.PlayerTickEvent;')
  s=s.replace('PlayerTickEvent event', 'PlayerTickEvent.'+phase+' event')
  s=s.replace('event.phase == Phase.START && ','').replace('event.phase == Phase.END && ','')
  s=s.replace('event.side == LogicalSide.CLIENT', 'event.getEntity().level().isClientSide')
  s=s.replace('event.player','event.getEntity()')
  f.write_text(s)
