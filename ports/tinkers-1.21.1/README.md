# Tinkers Construct → NeoForge 1.21.1 (unfinished)

No installable mod has been produced. Do not put these files in mods.

Inputs: user-provided TinkersConstruct-1.20.1.zip and Mantle-1.20.zip; hashes in PORT_STATUS.json.
The official Mantle 1.21 branch actually targets Minecraft 1.21.1; its exact source commit is pinned in mantle-upstream.json. Upstream authors retain all credit and licensing.

First patch: 116 ResourceLocation constructor calls changed to parse/fromNamespaceAndPath, including nested arguments; no tool mechanics changed. Apply resource-location.patch in the extracted TinkersConstruct-1.20.1 root using git apply. Alternatively run migrate_resource_locations.py with that root next to the script. Do not apply both.

The local build runner expects downloaded Gradle 9.2.1, Azul JDK21 under runtime, extracted pinned Mantle under upstream, and a runtime/build-cacerts truststore derived from the JDK defaults plus the environment CA. Those machine-specific dependencies and certificates are intentionally not committed.

Remaining: finish Mantle compilation, migrate TConstruct build/metadata to NeoForge, migrate tool NBT and capabilities, recipes, packets, fluids and rendering; compile and test client/server. ResourceId still subclasses the former ResourceLocation API and needs separate redesign. This checkpoint is not a completed port.
