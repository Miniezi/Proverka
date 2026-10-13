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

## World payloads (2026-10-12 UTC)

Validated source commit 1534141f05140b2127dc4314371495fb5f6a4388, run 38314682405. EntityMovementChangePacket and UpdateNeighborsPacket now use clientbound NeoForge payload registration and codecs. Receiving-world lookup replaces direct Minecraft singleton access; the erroneous server-sender gate on movement handling is removed. ExchangingModifier sends through PacketDistributor with a ServerPlayer guard. Legacy registrations for these packets are removed.

Ten isolated check groups pass. Added tests cover both codec roundtrips, actual velocity/rotation application, absent entities and defensive copying of mutable block positions. Both packet classes have no full-compile diagnostics; the whole source set still fails with 8,283 diagnostics. Neighbor-shape effects and connected-client behavior remain untested. No playable JAR.

## Complete registered network API migration (2026-10-13)

Validated commit b84a5e77d23a010dabf124d2d3f3c74e7ca74ef6, Actions run 38319071524. Migrated the remaining 27 payloads: all 30 play packets now have unique NeoForge payload IDs and direction-specific registration. TinkerNetwork has one registration owner and delegates typed sending to PacketDistributor. Chunk tracking, entity tracking, direct player delivery and serverbound delivery preserve their recipient scope. Material and datapack synchronization retain the integrated-server memory-connection exemption.

Moved four complex-spawn entities to IEntityWithComplexSpawn, removed obsolete spawn-packet overrides, migrated menu opening and registry-aware item serialization. Migrated the fluid entity serializer. Recipe packets now resolve IDs from RecipeHolder rather than removed Recipe.getId, and modifier sync uses the dynamic enchantment registry codec. Block-entity payload dispatch avoids loading missing chunks. Inventory updates validate slots and preserve item components.

The isolated server fixture passes all eleven marker groups, including new item/fluid, entity-fluid, recipe-ID and enchantment wire tests. Static checks found all 30 unique packet IDs and no remaining legacy NetworkHooks, NetworkWrapper, NetworkDirection, IThreadsafePacket, additional-spawn interface or PacketTarget references.

Full-source diagnostics decreased from 8,283 to 7,966. Remaining packet diagnostics refer to missing Lombok-generated constructors/getters in dependent uncompiled classes (tool menus, material stats, modifiers), rather than legacy network transport calls. This is not proof that all packet handlers work in-game. Full client/server connection, menu, projectile spawn and complete gameplay tests remain blocked by the unfinished full port. No playable JAR.


## Typed identifiers, registry aliases and contextual loadables (2026-10-13)

Validated source 9ff0e872df765873d8e1148813995306e399b229, Actions run 38371440369. Five typed resource-ID subclasses now use vanilla validation through a narrow NeoForge access transformer. The old SRG transformer list is retained only as reference. Eleven legacy registry aliases use ModifyRegistriesEvent without eagerly resolving deferred objects.

Migrated custom loadables, record fields and serialization callers to registry-aware buffers, contextual encode/serializeInto APIs, current stat registry encoding and dynamic enchantment descriptions. Twelve isolated server check groups pass, including ID equality/hash-map lookup, invalid ID rejection, built-in aliases, nested JSON, merged fields/lists and wire roundtrips. Full-source diagnostics decreased from 7,966 to 7,856. Custom alias targets, connected clients, old-world imports and the complete mod are not validated; no playable JAR.


## Quantity-aware recipe ingredients (2026-10-13)

Validated source 7d61975a2829fd6841ffd92606eac7a4d0f3304f, Actions run 38408564316, diagnostic artifact 11820411311. Migrated 50 consumer files and 84 Mantle fluid-object factory calls. TConstruct now owns the adapted MIT-licensed quantity-aware ingredient implementations; the original license and source revision are preserved in each source file. These are actual recipe implementations, not compile stubs.

Preserved the existing amount_needed item JSON format, empty sentinels, alternative fluids with different required quantities, common-tag equivalence and recipe display stacks. JSON item serialization now requires an explicit registry lookup context. Network serialization uses RegistryFriendlyByteBuf and current Mantle loadables. No old Mantle SizedIngredient/FluidIngredient imports remain in generated production sources.

Thirteen isolated server check groups pass. Ingredient checks cover item type/count rejection, exact thresholds, empty inputs, display-stack isolation, legacy flat/nested JSON, invalid zero JSON quantity, fluid alternatives, source/flowing water tags, legacy fluid names and sequential wire roundtrips. Full-source diagnostics decreased from 7,856 to 7,649; these counts include annotation-processing cascades and do not measure completion. New ingredient classes compile and execute in the fixture; their remaining full-source diagnostics concern Lombok-generated constructors/accessors amid the unresolved full project. No playable JAR.

Next major work: item components and ToolStack, modern recipe serializers/datagen/custom ingredients, remaining capability APIs and GUI/client migration. Full-mod and connected-client gameplay have not been tested.


## Material crafting serializers and bundled recipe data (2026-10-13)

Migrated ShapedMaterialsRecipe, ShapelessMaterialsRecipe and the deprecated ShapedMaterialRecipe to 1.21 MapCodec/StreamCodec serializers and ID-less vanilla recipe constructors. Recipe IDs belong to RecipeHolder. Preserved groups, categories, notifications, extra material order and shapeless part-count validation. Existing datagen helper constants remain available while the wider RecipeOutput port is pending.

Added the production MaterialRecipePattern codec: native pattern validation and shared key ingredient instances preserve repeated-part identity across JSON and registry-aware network roundtrips. Invalid symbols and malformed patterns return codec errors instead of escaping as exceptions. Custom component ingredients retain their component predicates.

Updated all 11 bundled material-crafting recipes: singular recipe resource directory, modern result id, and two legacy custom display names migrated to minecraft:custom_name. Other resource families and custom ingredient registration remain unported.

Validated source d8a094d89432fcbad3b18b0c45ff623a4e5fc280, Actions run 38413159293, artifact 11821154884. All 14 isolated check groups pass. Full-source diagnostics decreased from 7,649 to 7,599; this is not a completion percentage. The isolated fixture validates the production pattern codec, vanilla shaped matching, custom component ingredients and migrated result-name format; it does not execute the three material-aware recipes with ToolStack or all bundled mod items. Full-source compilation is still blocked by legacy custom ingredients, annotation-processing cascades and other unported subsystems. No playable JAR.


## Registered custom ingredients (2026-10-14, Asia/Yekaterinburg)

Migrated MaterialIngredient, MaterialValueIngredient, NoContainerIngredient and BlockTagIngredient to NeoForge ICustomIngredient/IngredientType registration. Factories return native Ingredient wrappers; material recipe and JEI consumers now unwrap with getCustomIngredient. Removed all legacy serializer references for these four types. Nested ingredient matching retains component-sensitive tests rather than treating every material ingredient as simple. Equality/hash behavior is defined, and obsolete per-instance display caches/invalidation hooks were removed in favor of native wrapper caching.

Added a backward-compatible nested ingredient codec: inline item/tag inputs are accepted; encoding uses an explicit match field to preserve nested custom ingredient types. Air and missing inputs are rejected. Material predicate handling retains compact IDs, structured predicates and legacy material_tag conjunction. Material quantities accept exact numbers or inclusive ranges with an omitted upper bound; negative/reversed/NaN bounds are rejected, and non-finite recipe quantities cannot match. Block-tag matching preserves shared item forms and excludes air.

The isolated fixture tests actual no-container and block-tag types through the registered Ingredient codecs, native wrappers, JSON and network roundtrips, nested component predicates, item and tag inputs, invalid input rejection, and exact/bounded/unbounded/fractional range codecs. MaterialIngredient/MaterialValueIngredient still depend on the unfinished material registry, recipe cache and item-component port; their full gameplay and reload behavior are not validated. Remaining custom ingredient ports include ToolHookIngredient and InstrumentIngredient. Full mod remains uncompiled; no playable JAR.

Validated source 86befaeca45c17c059b2cdbc6bf0eb4d03312166, Actions run 38479996232, artifact 11856158571. All 15 isolated check groups pass. Full-source diagnostics decreased from 7,599 to 7,476; this is not a completion percentage. MaterialIngredient, MaterialIngredientFilter, NestedIngredientCodec, NoContainerIngredient, BlockTagIngredient, MaterialValueRange and ShapedMaterialRecipe have no diagnostics in this run. MaterialValueIngredient retains dependent Lombok constructor/accessor errors; these were not replaced with manual stubs.
