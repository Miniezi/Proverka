# Unfinished TConstruct 1.21.1 NeoForge port

No playable JAR is available. Full compilation still fails.

Verified in Actions run 38161288525: pinned Mantle builds; the isolated display-context server fixture passes all six migrated contexts. The fixture is not the full mod.

Current fixes: identifier-boundary API renaming, preservation of project-owned FrameType, correct BiomeModifiers API name, Mantle ingredient loadables. Preparation validates public type filenames to catch accidental renaming.

Remaining major work: recipe codecs, item data components, capabilities, network payloads, GUI APIs, dynamic enchantment registries and access transformers. Client and full-mod gameplay tests have not run. Error counts include cascading failures and are not a completion percentage.

## Registration migration (2026-10-12)

Migrated single-item and single-block holders to DeferredItem/DeferredBlock in 15 Java files. Cast and geode wrappers remain multi-form Mantle ItemObject<Item, Item>; constructors now use registry holders. Advancement item consumers use ItemLike. Full integration is still pending; see Actions diagnostics, not a release.

## Entity data and equipment cache (2026-10-12)

Validated source commit d5e9acf3487023b407d0e7136d4490c60f8e67c0 in Actions run 38282086572. Seven isolated server check groups pass, including crafting offsets/remainders and actual migrated transient modifier attachments. Nonliving lookups return empty without allocating data. Entity isolation, identity-based keys, computed values and absence of save/load persistence are verified.

The client equipment watcher now keeps its per-player snapshot in the transient attachment, removing the old capability provider and invalidation plumbing. Original post-tick timing and copied ItemStack snapshots are retained. Client gameplay remains untested.

Full-source compilation still fails with 8,331 diagnostics, including cascading annotation-processing errors. No playable JAR. See PORT_STATUS.json for the latest verified checkpoint.

## Persistent modifier storage (2026-10-12)

Validated commit 50b558473c75d17bd340bcc1c32b881e0a25212d, Actions run 38290786334. PersistentDataCapability now wraps a serialized CompoundTag attachment with copyOnDeath. Consumers use optional lookups, retaining the living/projectile support checks. Registration occurs during mod construction; explicit login, respawn and dimension sync events remain. The obsolete capability clone/invalidation path was removed.

Eight isolated server check groups pass. New tests cover save/load, death and nondeath attachment copying, nested-data isolation, and omission of empty data. This tests the actual storage class, not the entire capability/network integration. Full compilation still reports 8,306 diagnostics. Packet migration and importing old Forge save data remain unvalidated. No playable JAR.

## Persistent-data payload (2026-10-12 UTC)

Validated commit 17ff1e2512d9ddb757bb55db1860f62eb92f887a in run 38300853009. SyncPersistentDataPacket uses CustomPacketPayload, a bounded FriendlyByteBuf NBT codec, clientbound registration and the receiving player from IPayloadContext. The sender uses PacketDistributor and rejects client-side invocation. Legacy channel registration for this packet is removed. Snapshots defensively copy NBT and replace the attachment contents in place, including clearing stale keys on empty updates.

Nine isolated server check groups pass. New checks cover registration, codec roundtrip, source/target isolation, replacement, empty clearing and stable attachment identity. The packet, persistent capability wrapper and attachment have no diagnostics in the full compile; the entire project still fails with 8,298 diagnostics. No connected-client synchronization test has run; no playable JAR.
