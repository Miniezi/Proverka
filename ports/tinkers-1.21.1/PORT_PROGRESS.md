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


## Instrument components and tool-hook ingredients (2026-10-14 UTC)

Validated source d89ba2c3a67ce996e7ef6e020eff8e64494f7496, Actions run 38546003854, artifact 11883789519. Migrated the final two legacy ingredient types to ICustomIngredient with registered MapCodec/registry-aware network codecs. All six original custom ingredient types now use native NeoForge registration and vanilla wrappers.

InstrumentIngredient reads DataComponents.INSTRUMENT instead of removed stack NBT APIs. Exact instrument keys and excluded tags are preserved, including the absent-component behavior for exclusions. Display stacks carry matching components; missing exact registry keys produce no fabricated display item. JSON requires a non-air item and exactly one selector. ToolHookIngredient evaluates current tool definitions and tags rather than reducing its predicate to cached item IDs; empty displays no longer fabricate barrier items.

All 15 isolated server check groups pass, including added actual instrument matching, missing/wrong components, excluded instrument tags, display validity, ambiguous/missing selector rejection, JSON and native wire roundtrips. InstrumentIngredient has zero full-source diagnostics. ToolHookIngredient has one dependent error: missing Lombok-generated ToolDefinition.getData(); its full tool-definition runtime remains unvalidated.

Full-source diagnostics decreased from 7,476 to 7,430. These counts include cascading failures and are not completion percentages. No playable JAR. Next major work remains ToolStack/item components, remaining recipe/datagen APIs and GUI/client migration.

## Material item component storage (2026-10-14 UTC)

Validated source f96434a4299fbf506bb0478c2d6947d699decaab, Actions run 38547441244, artifact 11885651119. Added production ItemStackData copy-on-write access to minecraft:custom_data. Reads return detached snapshots without creating components. Updates preserve unrelated custom keys, commit only after successful callbacks, remove empty components and avoid mutating ItemStack.EMPTY.

Migrated material writes in IMaterialItem, material reads in MaterialItem/MaterialBlockItem, and material-list reads/writes in MaterialIdNBT. Preserved existing Material/tic_materials field formats. Fixed negative-index handling in the direct material-list lookup. No manual replacement of Lombok methods or fake dependency implementations.

All 16 isolated server groups pass. The new group executes the real storage helper and verifies nested snapshot isolation, stack-copy isolation, atomic failure, name/damage preservation, empty-component cleanup, native item persistence and registry-aware item network roundtrips. ItemStackData, IMaterialItem and MaterialIdNBT have no full-source diagnostics. MaterialItem/MaterialBlockItem still require rarity, tooltip and load-hook API migration; this phase does not validate complete material-item gameplay or old-world imports.

Full-source diagnostics: 7,424 (previous 7,430). No playable JAR. ToolStack itself is deliberately NOT mechanically migrated: it retains live mutable NBT views used by persistent modifier data and raw-data hooks. Replacing those with snapshots without explicit commit semantics would silently lose updates. Remaining next work includes that live-view redesign, vanilla damage/unbreakable/name components, remaining recipes/datagen and client APIs.

## Material item lifecycle and tooltip API (2026-10-14 UTC)

Validated source 6acba706736151a49063c0cde3ba0933f9135f64, Actions run 38548556099, artifact 11885218357. MaterialItem and MaterialBlockItem now implement verifyComponentsAfterLoad and current TooltipContext signatures. Material writes, post-load verification and server inventory ticks refresh material redirects and the RARITY component after the material registry is ready. Unchanged values avoid component writes. This replaces the removed dynamic Item.getRarity override.

Added IMaterialItem.getMaterialRarity as the polymorphic policy used when refreshing the component. Migrated fake ingots, fake storage blocks and anvils to retain their explicit COMMON rarity policy. Migrated dependent tooltip overrides for tool parts, block parts, repair kits and anvils, including superclass/block calls. Ten source files are handled by the reproducible material migration script.

All 16 existing isolated server groups pass; no additional gameplay coverage is claimed for these lifecycle changes. The full compile reports zero diagnostics in MaterialItem, MaterialBlockItem, IMaterialItem, FakeIngotItem, FakeStorageBlockItem and AnvilBlockItem. Remaining errors in RepairKitItem/ToolPartItem/ToolPartBlockItem refer to previously missing generated dependency accessors. Full-source diagnostics are 7,416, versus 7,424 before this phase. The first run exposed dependent tooltip/rarity overrides; the follow-up fixed them rather than suppressing overrides.

No playable JAR. Complete material-registry reload behavior, client tooltip rendering, container-held item refresh, old-world imports and ToolStack's mutable data contract remain unvalidated or unfinished. ToolStack itself has not yet been ported to components.

## Mutable modifier data publication foundation (2026-10-14 UTC)

Validated source c08f1b474f516e6139603e1df86778464e480675, Actions run 38549380130, artifact 11885773459. Added production ModifierDataStorage for detached snapshot publication, self-copy-safe replacement preserving working compound identity, and nested edit transactions that commit only after the editing callback succeeds.

ModDataNBT mutators and ToolDataNBT slot writes now notify an optional owner callback. Existing constructors retain their live-data behavior and do not allocate publication snapshots when no callback is attached. New factory overloads allow a future component owner to receive snapshots. Observer state is excluded from value equality. copyFrom now snapshots its input before clearing the target, fixing self-copy data loss. ModifierSetWorktableRecipe explicitly writes back a nonempty list after removal, preparing it for detached reads and ensuring owner notification.

All 17 isolated server groups pass. The new group tests the actual ModifierDataStorage implementation: snapshot isolation, self-copy, replacement cleanup, nested changes and failed-edit rollback. It does not execute the entire ModDataNBT/ToolDataNBT API because their SlotType/tool-stat dependencies are still unported. ModifierDataStorage and ModDataNBT have no full-source diagnostics; ToolDataNBT retains the preexisting missing generated getData/getName accessor errors. Full-source diagnostics: 7,413 (previous 7,416).

This is a foundation, not a completed ToolStack migration: no ItemStack component owner is bound yet. Legacy mutable getter results still exist and changes through those references do not automatically publish. Remaining callers (inventory lists, ranged ammo, raw-data hooks) must be audited or converted to explicit edits before enabling component binding. No playable JAR.

## Detached tool inventory edits (2026-10-14 UTC)

Validated source 8da6daff5846e366a4ed4f21a73248f74aa8a01e, Actions run 38602574085, artifact 11915190942. InventoryModule.setStack now builds a detached list and publishes its completed contents through ModDataNBT.put/remove. Previously a newly created list could be published before insertion, and existing list changes never notified the new owner callback. Failed serialization cannot partially clear a stored stack. Empty lists are removed.

Added production ToolInventoryData: copied insertion/replacement/removal, and atomic slot fitting that retains valid indices and relocates negative, missing, duplicate or out-of-range indices. Fitting rejects insufficient capacity without changing the input. Ordinary edits retain additional entries even in corrupted duplicate-slot input; validation can relocate those entries instead of silently dropping them. Inventory reads now reject negative indices before array access. Validation publishes only after successful fitting.

All 18 isolated server groups pass. New tests execute the real list-editing helper and cover input/replacement isolation, insert/replace/remove, relocation, duplicate and negative slots, zero/negative/insufficient capacity, and unchanged input after rejection. ToolInventoryData has zero full-source diagnostics. InventoryModule still has existing item serialization API and generated accessor/constructor failures. Complete item serialization, tool capabilities, live ToolStack ownership and gameplay are not validated by these tests.

Full-source diagnostics remain 7,413. No playable JAR. This phase fixes mutation publication and validation behavior; it does not claim the complete inventory or ToolStack port is finished.

## Registry-aware stored ammunition (2026-10-14 UTC)

Validated source edc10d9f5330f49d349be3d5272f2f1f9367af18, Actions run 38612850335, artifact 11917673216. Added production StoredItemStack using the native ItemStack codec with an explicit HolderLookup.Provider. Encoding completes before callers replace their stored tag; empty stacks use an empty compound. Reading uses vanilla parseOptional with its invalid-item fallback. No global registry singleton or built-in-only lookup was substituted for the world's dynamic registries.

Migrated three ammo writes in ModifiableBowItem/ModifiableCrossbowItem and the crossbow firing read to the owning level's registry access. This retains item components including dynamically registered enchantment holders. Context-free tooltip decoding and InventoryModule serialization remain unchanged until lookup context is threaded through those APIs; the ranged item classes retain other unported gameplay APIs.

All 19 isolated server groups pass. The new group executes actual StoredItemStack against dedicated-server registries, covering count, custom name/data, a dynamic enchantment, source/decoded stack isolation, empty sentinels and unknown-item fallback. It does not test full bow/crossbow gameplay, ToolStack ownership or old-format data migration. StoredItemStack has zero full-source diagnostics. Full-source diagnostics decreased from 7,413 to 7,409. No playable JAR.

## Projectile launch API (2026-10-14 UTC)

Validated source ba6b0db4e4d9778d250cb5bbc96f1b76495ca7fa, Actions run 38614147603, artifact 11918484550. Implemented ProjectileWeaponItem's new shootProjectile entry point in ModifiableLauncherItem using a production ProjectileAim helper. It supports view-based angular spread and an optional target with elevation compensation. Existing crossbow player shooting shares the same view-axis rotation and retains its existing speed, accuracy and angles. Existing bow player release logic is retained.

Both bow and crossbow arrow factories receive the actual firing ItemStack required by 1.21.1. Migrated the trident sound holder access and nested crossbow tooltip context. The removed setShotFromCrossbow call is deliberately still an explicit outstanding compile failure until its replacement semantics for modded weapons are verified. Context-free ammo tooltip decoding and the broader ranged item APIs remain unfinished.

All 20 isolated server groups pass. The new fixture checks actual projectile velocity against the shooter's view, symmetric angular spread, speed, targeted direction and native arrow owner assignment. The first run failed because its fixed world-axis expectation did not match the fixture shooter's view; the corrected test initializes head rotation and checks the actual view vector rather than assuming a world axis. The production launch implementation was unchanged between those runs.

ProjectileAim has zero full-source diagnostics; full-source diagnostics are 7,405 (previous 7,409). These checks do not cover modifier damage/effects, crossbow attribution, ammunition consumption, mob AI integration or complete ranged gameplay. No playable JAR.

## Crossbow lifecycle and shared durability API (2026-10-15 Asia/Yekaterinburg)

Validated source 9a42abc0f8c97a9a543d13eebe1989f81c168339, Actions run 38645053039, artifact 11931892286. Intermediate crossbow source 54024f2f7e63a9819acdaab1e16f9339fe097d31 and shared durability source 47d8e383ce832e1a0766d5cddc9eb3bc56fdbcbb were followed by the complete validation run. Local diagnostics: run47 and run48.

Inspected Mojang's official 1.21.1 client and mappings: AbstractArrow.shotFromCrossbow tests its saved firedFromWeapon against Items.CROSSBOW, not a mutable boolean. Added a narrowly scoped required RETURN mixin that retains true vanilla results and recognizes the tconstruct:modifiable/ranged/crossbows item tag. It uses the actual saved weapon, with no fake vanilla weapon replacement. Removed the obsolete setter. Migrated the bundled crossbow tag to tags/item and registered the mixin in both production metadata and the explicitly separate fixture.

Migrated the launcher use-duration override and bow/crossbow calls to include the living entity. Crossbow ammo tooltip decoding now uses the player's registry access or Mantle's guarded client-world lookup, preserving components/enchantments. With no available world, detailed nested ammo decoding is skipped without altering stored data.

Migrated shared durability APIs in ModifiableItem, ModifiableArmorItem, ModifiableLauncherItem and ToolDamageUtil: item-stack-sensitive isDamageable, Consumer<Item> break callbacks, raw broken-flag custom-data reads/writes, current tooltip contexts, and onEquippedItemBroken for equipment and hand animations. Existing custom durability calculation remains; this does not replace ToolStack with vanilla durability or delete broken tools.

All 21 isolated server groups pass. Added actual native arrow attribution checks for vanilla crossbows, a tagged fixture item, ordinary bows and no weapon, plus saved/reloaded weapon attribution. The mixin executes in the dedicated-server fixture. Full-source diagnostics decreased from 7,405 to 7,383; ToolDamageUtil and AbstractArrowMixin now have zero diagnostics. Ranged subclasses retain generated accessor/dependency errors; the base item classes still require other component/capability migration.

Limitations: full damage/repair gameplay, client tooltip rendering, advancement awards, multiplayer and a distributable production JAR remain untested or blocked by the unfinished full port. ToolStack component ownership is not complete. No playable JAR.

## Nested modifier mutation publication (2026-10-14 UTC)

Validated source 2a008d763872a4a01835d8d81f20cada30aafba6, Actions run 38645912953, artifact 11931793879, local run49. Added guarded migration for StatOverrideModifier, ToggleInteractionWorktableRecipe and ModifierSetWorktableRecipe.

Stat edits now copy existing nested compounds and publish only after writing the new value. Neutral-value removal republishes remaining stats, and removal of the last stat clears the group. Generic stat serialization finishes before publication, avoiding publication of an empty group if serialization throws. Existing return semantics remain unchanged.

Worktable set edits use detached lists. Interaction toggling computes both lists before publishing them together through ModDataNBT.edit, preserving unrelated persistent data and explicitly clearing empty lists. This removes dependence on mutating getter-returned references.

Source preparation and all 21 existing isolated server groups pass. Full compilation remains failed with 7,381 diagnostics (previous 7,383; fewer repeated getter call sites, not evidence that another subsystem compiles). These three full gameplay classes still have generated-accessor and worktable-constructor dependency errors. Existing storage transaction tests pass, but do not execute these worktable/stat classes. No claim of end-to-end gameplay validation or a playable JAR.

Next: complete mutable nested-data audit, including SmeltingModule and RestrictedCompoundTag hooks, before binding ToolStack to item components. Smelting input/output key aliasing and explicit registry context for InventoryModule serialization require care; they were inspected but not modified in this block.

## Restricted raw-data boundaries (2026-10-15 UTC)

Validated source 6c92f68c03d7e55d12cb2d1f4cab1f26eab47e2b, Actions run 38708062406, artifact 11959042350, local run50. RestrictedCompoundTag now has explicit constructors and an optional snapshot publication callback. Mutable tag/compound/list getters return detached copies and put() copies its input. All allowed mutators notify the owner when one is supplied. The restricted key set is copied to prevent later caller changes from removing protections.

Added edit(Consumer<RestrictedCompoundTag>) for successful all-at-once edits. A failing editor leaves root data unchanged and sends no publication; retained editors cannot mutate the committed tree. Protected fields remain inaccessible within the editor. ToolStack.refreshTag also invalidates its cached restricted wrapper after replacing the underlying NBT.

Audited all bundled RawDataModifierHook implementations (HeadlightModule, TheOneProbeModule and EmbellishmentModule). None depend on mutable getter results. Compatibility note for future ported addons: modify a returned snapshot and explicitly put it back, or use edit(); nested getter mutation alone no longer changes the tool.

All 22 isolated server marker groups pass, including the actual migrated RestrictedCompoundTag class. New tests cover restricted reads/writes, externally modified key sets, compound/list/input/publication aliasing, retained editors, atomic commit, and exception rollback. RestrictedCompoundTag has zero full-source diagnostics. Full compilation still fails with 7,380 diagnostics (previous 7,381). ToolStack's cache invalidation is source-reviewed but cannot be gameplay-tested until its component migration and dependencies are complete.

No playable JAR. The optional raw-data publication callback is not yet bound to ToolStack's component owner. Smelting/inventory registry context, ToolStack ownership, native vanilla component semantics and full gameplay integration remain outstanding.

## Transparent glass blocks and codecs (2026-10-15 UTC)

Validated source b1aa6c7b3174ea68dd703523a14cfd39577009d0, Actions run 38720417830, artifact 11964910592, local run53. Production migration introduced in af865371ba7ad92fa1b91353e13f07ffbf1f8557; two subsequent commits correct fixture API access and block registration timing.

Migrated removed AbstractGlassBlock/GlassBlock references to TransparentBlock in ClearStainedGlassBlock, SoulGlassBlock and TinkerCommons registration. Colored full blocks and panes now return opaque Integer ARGB values for NeoForge beacon tinting. Added concrete MapCodecs for ClearStainedGlassBlock, ClearStainedGlassPaneBlock, SoulGlassBlock, BetterPaneBlock and ClearGlassPaneBlock; colored codecs preserve the original GlassColor enum rather than substituting vanilla dye colors. Migrated SoulGlassBlock's pathfinding override to the current signature, retaining its false result and solid support shape.

All 23 isolated server groups pass. The actual five block classes compile and execute in the fixture. Tests register original and codec-decoded block instances during RegisterEvent (before registry freeze), check all 16 colors for blocks and panes, roundtrip all five codecs, test adjacent glass and vertical pane culling, and check soul-glass pathfinding and support. First attempts caught fixture-only issues: a protected block method must be called through BlockState, and block construction after registry freeze is invalid. Production code was unchanged during these fixture fixes.

Full compilation remains failed with 7,359 diagnostics, down from 7,380. The five migrated block classes have no full-source diagnostics. TinkerCommons still has unrelated dependency/registration failures. No client connected-texture rendering, complete block-type codec registry integration, actual beacon beam averaging or full mod gameplay has been validated. No playable JAR. SearedSoulGlassBlock and other smeltery block APIs remain separate unfinished work.

## Block pathfinding and seared codecs (2026-10-15 UTC)

Validated source 5f8704d287549844c8b685ae8053f4e6787084a8, Actions run 38727710625, artifact 11969460466, local run54. Updated 15 source classes. Replaced BlockPathTypes with PathType while preserving each hazard classification. Migrated six remaining constant-false isPathfindable overrides to the current two-argument signature: TableBlock, SlimesteelBlock, ChannelBlock, FaucetBlock, SearedSoulGlassBlock and CongealedSlimeBlock. NeoForge IBlockExtension source confirms the PathType hook signature.

Added concrete codecs for SearedBlock, SearedGlassBlock, SearedTintedGlassBlock and SearedSoulGlassBlock. The base codec explicitly encodes required_block_entity, preserving the distinction between always-present and structure-dependent block entities. Subclass codecs retain their constructors and specialized behavior. No structure notification or block entity lifecycle logic was removed.

Preparation succeeds; all 23 existing isolated server groups still pass. Full-source diagnostics decrease from 7,359 to 7,327. The four seared classes now have no full-source diagnostics. These classes are not in the isolated runtime fixture: codec roundtrips, smeltery structure behavior, navigation and lighting still need actual gameplay/integration validation. Full mod compilation remains failed and there is no playable JAR.

## Dispenser source and placement components (2026-10-15 UTC)

Validated source 695dbe7968bdd6c371f3e033c3bda57bf27153a8, Actions run 38730688347, artifact 11970160479, local run55. Migrated all six BlockSource consumers to net.minecraft.core.dispenser.BlockSource and its record accessors. Fancy armor stand spawning uses the current consumer overload and retains appendDefaultStackConfig to apply the item configuration. Official local 1.21.1 mappings confirm these signatures.

PlaceBlockDispenserBehavior resets its success flag for each attempt, requires successful block placement before consuming an item, and applies ItemStack components to the created block entity after its custom block-entity tag. Existing placement callbacks, game event and sound remain. This preserves named block entities in the new component format and prevents consumption on rejected placement.

All 24 isolated server groups pass. New checks execute the production placement behavior in a dedicated-server world with vanilla blocks: successful stone placement consumes one item; an occupied target does not consume another; a named chest transfers its custom name; a non-block item remains unchanged. The test clears its temporary dispenser and target afterward. It does not exercise protection-mod cancellation, multiblock placement or the fancy armor stand/projectile behaviors.

Full-source diagnostics decrease from 7,327 to 7,313. PlaceBlockDispenserBehavior, DispenseFancyArmorStand and ModifiableShurikenDispenserBehavior have no diagnostics in this run; ShootProjectileDispenserBehavior retains a generated-constructor dependency error. These facts do not establish complete gameplay integration. Full compilation still fails; no playable JAR.

## Block entity persistence lifecycle (2026-10-15 UTC)

Validated source e0d7762a522f5a84e60aa00c38a8692d793bf569, Actions run 38751529628, artifact 11981692146, local run56. Migrated 45 lifecycle methods in 20 block entity classes across tables, chests, material blocks and smeltery components/controllers. Added HolderLookup.Provider parameters to loadAdditional, saveAdditional, saveSynced and getUpdateTag, forwarding the same provider through superclass and Mantle inventory serialization calls inside those methods. Mantle's pinned source confirms these signatures. The migration edits lifecycle bodies only; it does not insert a global registry singleton.

All 24 existing isolated server groups pass. Full-source diagnostics decrease from 7,313 to 7,240. TableBlockEntity's persistence API errors are gone; its existing Sounds getter error remains. These changed block entities are not directly exercised by the isolated fixture. Nested fluid/item serialization helpers, other callers of renamed methods and remaining block entity dependencies are still follow-up work. No claim of successful world save/reload or multiplayer synchronization. Full compilation remains failed; no playable JAR.

## Core melting storage (2026-10-15 UTC)

User priority: focus on usable core mechanics (tools, modifiers, melting/alloying/casting). Defer decorative blocks and cosmetic work unless strictly required to unblock the core build.

Validated source 0bed63298b546be22c501f64a9e117b9be46e694, Actions run 38752696788, artifact 11982052500, local run57. Threaded explicit registry providers from MelterBlockEntity and HeatingStructureBlockEntity through MeltingModuleInventory into MeltingModule item serialization. Uses the already tested production StoredItemStack codec so item components and dynamic enchantment holders survive storage. Existing slot layout, current heat progress, required time and temperature fields are retained. Loading an empty/invalid item now clears stale progress fields. Migrated the melter's FluidTank read/write calls to provider-aware API.

All 24 existing isolated server groups pass; full-source diagnostics are 7,235 (previous 7,240). No diagnostics involving the new registry-aware melting persistence calls were reported. The affected classes retain other recipe/capability/generated-accessor errors. Existing StoredItemStack checks validate the shared codec, not full melting-module gameplay. Complete melting, fuel consumption, alloying and casting are not yet runtime validated. No playable JAR.

Next core blockers: recipe-holder lookup and recipe codecs, fluid/item capabilities and tank connections, then an actual server test of melting and casting. ToolStack component ownership remains another primary blocker. No cosmetic work is planned.
