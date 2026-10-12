"""Migrate the complete registered packet set to NeoForge custom payloads."""
import re

def migrate(root):
 java=root/'src/main/java'
 network=java/'slimeknights/tconstruct/common/network/TinkerNetwork.java'
 old=network.read_text()
 registrations=re.findall(r'instance\.registerPacket\((\w+)\.class, (.*?), NetworkDirection\.(PLAY_TO_CLIENT|PLAY_TO_SERVER)\);',old)
 assert len(registrations)==27,len(registrations)
 paths={p.stem:p for p in java.rglob('*Packet.java')}
 entries=[]
 for name,decoder,direction in registrations:
  f=paths[name];s=f.read_text()
  s=s.replace('import slimeknights.mantle.network.packet.IThreadsafePacket;', 'import slimeknights.tconstruct.common.network.TinkerPacket;')
  s=s.replace('import slimeknights.mantle.network.packet.BlockEntityPacket;', 'import slimeknights.tconstruct.common.network.TinkerBlockEntityPacket;')
  s=s.replace('IThreadsafePacket','TinkerPacket').replace('implements BlockEntityPacket<','implements TinkerBlockEntityPacket<')
  s=s.replace('import net.neoforged.neoforge.network.NetworkEvent.Context;', 'import net.neoforged.neoforge.network.handling.IPayloadContext;')
  s=re.sub(r'\bContext\b','IPayloadContext',s)
  s=s.replace('handleThreadsafe(', 'handle(')
  s=s.replace('context.getSender()', '(context.player() instanceof ServerPlayer serverPlayer ? serverPlayer : null)')
  s=re.sub(r'\bFriendlyByteBuf\b','RegistryFriendlyByteBuf',s)
  s=re.sub(r'(public Class<[^>]+>) type\(\)',r'\1 blockEntityType()',s)
  s=re.sub(r'(\w+)\.readItem\(\)',r'net.minecraft.world.item.ItemStack.OPTIONAL_STREAM_CODEC.decode(\1)',s)
  s=re.sub(r'(\w+)\.writeItem\(([^;]+)\);',r'net.minecraft.world.item.ItemStack.OPTIONAL_STREAM_CODEC.encode(\1, \2);',s)
  s=re.sub(r'(\w+)\.readFluidStack\(\)',r'net.neoforged.neoforge.fluids.FluidStack.OPTIONAL_STREAM_CODEC.decode(\1)',s)
  s=re.sub(r'(\w+)\.writeFluidStack\(([^;]+)\);',r'net.neoforged.neoforge.fluids.FluidStack.OPTIONAL_STREAM_CODEC.encode(\1, \2);',s)
  s=s.replace('import net.neoforged.neoforge.network.NetworkHooks;\n','')
  s=s.replace('NetworkHooks.openScreen(sender, provider, pos)', 'sender.openMenu(provider, pos)')
  if name=='StationTabPacket':
   s=s.replace('    if (sender != null) {','    if (sender != null) {\n      if (!sender.level().hasChunkAt(pos)) return;')
  identifier=re.sub(r'(?<!^)(?=[A-Z])','_',name).lower()
  fields=f'''\n  public static final net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<{name}> TYPE = new net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<>(net.minecraft.resources.ResourceLocation.fromNamespaceAndPath("tconstruct", "{identifier}"));
  public static final net.minecraft.network.codec.StreamCodec<net.minecraft.network.RegistryFriendlyByteBuf, {name}> CODEC = net.minecraft.network.codec.StreamCodec.of((buf, packet) -> packet.encode(buf), {decoder});
  @Override public net.minecraft.network.protocol.common.custom.CustomPacketPayload.Type<{name}> type() {{ return TYPE; }}
'''
  # Insert after enum constants, or directly after the outer class/record declaration.
  decl=re.search(r'public (?:class|record|enum) '+name+r'\b[^\{]*\{',s);assert decl,name
  pos=decl.end()
  if 'public enum '+name in s:pos=s.index(';',pos)+1
  s=s[:pos]+fields+s[pos:];f.write_text(s)
  fqcn=re.search(r'package ([^;]+);',s).group(1)+'.'+name
  method='playToClient' if direction=='PLAY_TO_CLIENT' else 'playToServer'
  entries.append(f'    registrar.{method}({fqcn}.TYPE, {fqcn}.CODEC, (packet, context) -> packet.handle(context));')
 # Single registration owner for all payloads, including the three earlier migrations.
 registrations_code='\n'.join(entries)
 network.write_text('''package slimeknights.tconstruct.common.network;

import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import slimeknights.tconstruct.TConstruct;

/** Registration and typed transport for all TConstruct play payloads. */
public final class TinkerNetwork extends TinkerPacketSender {
  private static TinkerNetwork instance;
  private TinkerNetwork() {}
  public static TinkerNetwork getInstance() {
    if (instance == null) throw new IllegalStateException("Network is not initialized");
    return instance;
  }
  public static void setup() {
    if (instance != null) return;
    instance = new TinkerNetwork();
    TConstruct.getModEventBus().addListener(TinkerNetwork::register);
  }
  private static void register(RegisterPayloadHandlersEvent event) {
    var registrar = event.registrar("1");
'''+registrations_code+'''
    SyncPersistentDataPacket.register(event);
    UpdateNeighborsPacket.register(event);
    slimeknights.tconstruct.tools.network.EntityMovementChangePacket.register(event);
  }
}
''')
 # Remove earlier standalone registration, now owned by TinkerNetwork.
 f=java/'slimeknights/tconstruct/tools/TinkerModifiers.java';s=f.read_text();s=''.join(l for l in s.splitlines(True) if 'addListener(slimeknights.tconstruct.common.network.SyncPersistentDataPacket::register)' not in l);f.write_text(s)
 return {'packets':len(registrations)+3,'migrated_now':len(registrations)}
