"""Register migrated world payloads and update their active send sites."""
def migrate(root):
 java=root/'src/main/java/slimeknights/tconstruct'
 f=java/'common/network/TinkerNetwork.java';s=f.read_text()
 s=''.join(line for line in s.splitlines(True) if not any('instance.registerPacket('+name+'.class' in line for name in ['UpdateNeighborsPacket','EntityMovementChangePacket']))
 s=s.replace('    instance = new TinkerNetwork();','    instance = new TinkerNetwork();\n    TConstruct.getModEventBus().addListener(UpdateNeighborsPacket::register);\n    TConstruct.getModEventBus().addListener(EntityMovementChangePacket::register);');f.write_text(s)
 f=java/'tools/modifiers/ability/tool/ExchangingModifier.java';s=f.read_text().replace('TinkerNetwork.getInstance().sendTo(new UpdateNeighborsPacket(state, pos), player);','if (player instanceof net.minecraft.server.level.ServerPlayer serverPlayer) {\n          net.neoforged.neoforge.network.PacketDistributor.sendToPlayer(serverPlayer, new UpdateNeighborsPacket(state, pos));\n        }');f.write_text(s)
 return 2
