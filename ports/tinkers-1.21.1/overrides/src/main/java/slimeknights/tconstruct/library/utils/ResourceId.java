package slimeknights.tconstruct.library.utils;

import net.minecraft.resources.ResourceLocation;
import javax.annotation.Nullable;
import java.util.function.BiFunction;

/** Typed resource identifiers. The narrow access transformer preserves the existing subtype API. */
public abstract class ResourceId extends ResourceLocation {
  public ResourceId(ResourceLocation location) { super(location.getNamespace(), location.getPath()); }
  public ResourceId(String namespace, String path) { this(ResourceLocation.fromNamespaceAndPath(namespace, path)); }
  public ResourceId(String location) { this(ResourceLocation.parse(location)); }

  @Nullable
  protected static <T extends ResourceLocation> T tryParse(String string, BiFunction<String,String,T> constructor) {
    ResourceLocation parsed = ResourceLocation.tryParse(string);
    return parsed == null ? null : constructor.apply(parsed.getNamespace(), parsed.getPath());
  }
  @Nullable
  protected static <T extends ResourceLocation> T tryBuild(String namespace, String path, BiFunction<String,String,T> constructor) {
    ResourceLocation parsed = ResourceLocation.tryBuild(namespace, path);
    return parsed == null ? null : constructor.apply(parsed.getNamespace(), parsed.getPath());
  }
}
