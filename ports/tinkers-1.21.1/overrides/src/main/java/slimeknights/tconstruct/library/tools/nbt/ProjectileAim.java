package slimeknights.tconstruct.library.tools.nbt;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import javax.annotation.Nullable;

/** Shared aiming implementation for the 1.21 projectile-weapon entry point. */
public final class ProjectileAim {
  private ProjectileAim() {}

  public static void shoot(LivingEntity shooter, Projectile projectile, float speed,
                           float inaccuracy, float angle, @Nullable LivingEntity target) {
    Vec3 direction = shooter.getViewVector(1.0F);
    if (target != null) {
      double dx = target.getX() - shooter.getX();
      double dz = target.getZ() - shooter.getZ();
      double dy = target.getY(1.0D/3.0D) - projectile.getY();
      Vec3 aimed = new Vec3(dx, dy + Math.sqrt(dx*dx + dz*dz)*0.2D, dz);
      if (aimed.lengthSqr() > 1.0E-12D) direction = aimed.normalize();
    }
    Vec3 up = shooter.getUpVector(1.0F);
    Vector3f rotated = direction.toVector3f().rotate(new Quaternionf()
      .setAngleAxis(angle * Math.PI / 180D, up.x, up.y, up.z));
    projectile.shoot(rotated.x(), rotated.y(), rotated.z(), speed, inaccuracy);
  }
}
