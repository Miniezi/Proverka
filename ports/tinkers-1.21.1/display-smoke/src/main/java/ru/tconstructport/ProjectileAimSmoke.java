package ru.tconstructport;

import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.projectile.Snowball;
import net.minecraft.world.item.ArrowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import slimeknights.tconstruct.library.tools.nbt.ProjectileAim;

final class ProjectileAimSmoke {
  static void validate(net.neoforged.neoforge.event.server.ServerStartedEvent event) {
    var level = event.getServer().overworld();
    var shooter = new ArmorStand(level,0,64,0);
    shooter.setXRot(0); shooter.setYRot(0);
    var straight = new Snowball(level,shooter);
    ProjectileAim.shoot(shooter,straight,3,0,0,null);
    var v=straight.getDeltaMovement();
    if (Math.abs(v.length()-3)>1e-5 || Math.abs(v.x)>1e-5 || v.z<2.99) fail("straight launch");
    var left = new Snowball(level,shooter); var right = new Snowball(level,shooter);
    ProjectileAim.shoot(shooter,left,3,0,-10,null);
    ProjectileAim.shoot(shooter,right,3,0,10,null);
    if (Math.abs(left.getDeltaMovement().x+right.getDeltaMovement().x)>1e-5
        || left.getDeltaMovement().x*right.getDeltaMovement().x>=0
        || Math.abs(left.getDeltaMovement().length()-3)>1e-5) fail("angular spread");
    var target = new ArmorStand(level,10,64,0);
    var aimed = new Snowball(level,shooter);
    ProjectileAim.shoot(shooter,aimed,2,0,0,target);
    if (aimed.getDeltaMovement().x<=0 || Math.abs(aimed.getDeltaMovement().z)>1e-5
        || Math.abs(aimed.getDeltaMovement().length()-2)>1e-5) fail("target aim");
    var arrow = ((ArrowItem)Items.ARROW).createArrow(level,new ItemStack(Items.ARROW),shooter,new ItemStack(Items.CROSSBOW));
    if (arrow.getOwner()!=shooter) fail("arrow owner");
    System.out.println("TCONSTRUCT_PROJECTILE_AIM_OK direction=1 spread=1 target=1 arrow=1");
  }
  private static void fail(String message) {throw new IllegalStateException(message);}
}
