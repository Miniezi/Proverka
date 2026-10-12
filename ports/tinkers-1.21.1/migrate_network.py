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
  if name=='UpdateModifiersPacket':
   s=s.replace('import net.neoforged.neoforge.registries.ForgeRegistries;\n','')
   s=s.replace('buffer.readRegistryIdUnsafe(ForgeRegistries.ENCHANTMENTS)', 'slimeknights.tconstruct.common.network.TinkerPacketCodecs.ENCHANTMENT.decode(buffer)')
   s=s.replace('buffer.writeRegistryIdUnsafe(ForgeRegistries.ENCHANTMENTS, entry.getKey())', 'slimeknights.tconstruct.common.network.TinkerPacketCodecs.ENCHANTMENT.encode(buffer, entry.getKey())')
  if name in ['UpdateCraftingRecipePacket','UpdateTinkerStationRecipePacket']:
   recipe_type='CraftingRecipe' if name=='UpdateCraftingRecipePacket' else 'ITinkerStationRecipe'
   s=s.replace('import slimeknights.mantle.recipe.helper.RecipeHelper;\n','')
   s=s.replace('BlockPos pos, '+recipe_type+' recipe)', 'BlockPos pos, ResourceLocation recipe)')
   s=s.replace('this.recipe = recipe.getId();','this.recipe = recipe;')
   s=re.sub(r'RecipeHelper.getRecipe\(([^,]+), ([^,]+), '+recipe_type+r'\.class\)',r'\1.byKey(\2).map(net.minecraft.world.item.crafting.RecipeHolder::value).filter('+recipe_type+'.class::isInstance).map('+recipe_type+'.class::cast)',s)
   s=s.replace('BlockEntityPacket.getBlockEntity(world, packet.pos, packet)', '(world.hasChunkAt(packet.pos) ? world.getBlockEntity(packet.pos) : null)')
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
 spawn_count=0
 for f in java.rglob('*.java'):
  s=f.read_text();before=s
  if 'IEntityAdditionalSpawnData' in s:
   s=s.replace('IEntityAdditionalSpawnData','IEntityWithComplexSpawn')
   s=re.sub(r'\bFriendlyByteBuf\b','RegistryFriendlyByteBuf',s)
   s=re.sub(r'(\w+)\.readItem\(\)',r'net.minecraft.world.item.ItemStack.OPTIONAL_STREAM_CODEC.decode(\1)',s)
   s=re.sub(r'(\w+)\.writeItem\(([^;]+)\);',r'net.minecraft.world.item.ItemStack.OPTIONAL_STREAM_CODEC.encode(\1, \2);',s)
   spawn_count+=1
  if 'NetworkHooks' in s:
   s=re.sub(r'  (?:@Nonnull\s+)?@Override\s+public Packet<ClientGamePacketListener> getAddEntityPacket\(\) \{\s+return NetworkHooks.getEntitySpawningPacket\(this\);\s+\}', '', s)
   s=re.sub(r'NetworkHooks.openScreen\((\w+), ',r'\1.openMenu(',s)
   s=s.replace('import net.neoforged.neoforge.network.NetworkHooks;\n','')
  s=s.replace('import slimeknights.mantle.network.packet.ISimplePacket;', 'import slimeknights.mantle.network.ISimplePacket;')
  if f.name in ['CraftingStationBlockEntity.java','TinkerStationBlockEntity.java']:
   s=re.sub(r'TinkerNetwork.getInstance\(\).sendTo\(new (Update(?:Crafting|TinkerStation)RecipePacket)\(this.worldPosition, this.lastRecipe\), ([^;]+)\);',r'slimeknights.tconstruct.common.network.RecipeNetworkLookup.findId(this.level.getRecipeManager(), this.lastRecipe).ifPresent(id -> TinkerNetwork.getInstance().sendTo(new \1(this.worldPosition, id), \2));',s)
  if f.name=='MaterialRegistry.java':
   s=s.replace('import net.neoforged.neoforge.network.PacketDistributor.PacketTarget;\n','')
   s=s.replace('      PacketTarget target = PacketDistributor.PLAYER.with(() -> player);\n','')
   s=s.replace('network.send(target, packet)', 'network.sendTo(packet, player)')
   s=s.replace('player.connection.connection.isMemoryConnection()', 'player.connection.getConnection().isMemoryConnection()')
  if f.name=='JsonUtils.java':
   s=s.replace('JsonHelper.syncPackets(event, TinkerNetwork.getInstance(), packets);', 'if (packets.length > 0) slimeknights.mantle.network.PacketHelper.syncPackets(event, packets[0], java.util.Arrays.copyOfRange(packets, 1, packets.length));')
  if f.name=='ToolInventoryCapability.java':
   s=s.replace('buf.writeItem(stack);','net.minecraft.world.item.ItemStack.OPTIONAL_STREAM_CODEC.encode(buf, stack);')
  if f.name=='ToolContainerMenu.java':
   s=re.sub(r'\bFriendlyByteBuf\b','RegistryFriendlyByteBuf',s)
   s=s.replace('buffer.readItem()', 'ItemStack.OPTIONAL_STREAM_CODEC.decode(buffer)')
  if s!=before:f.write_text(s)
 return {'packets':len(registrations)+3,'migrated_now':len(registrations),'complex_spawn_entities':spawn_count}
