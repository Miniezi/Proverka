"""Implement the native projectile-weapon launch hook and pass actual firing items."""
def migrate(root):
    folder=root/'src/main/java/slimeknights/tconstruct/library/tools/item/ranged'
    p=folder/'ModifiableLauncherItem.java';s=p.read_text()
    marker='  /* Basic properties */'
    s=s.replace(marker,'''  @Override
  protected void shootProjectile(LivingEntity shooter, net.minecraft.world.entity.projectile.Projectile projectile,
                                 int index, float speed, float inaccuracy, float angle, @Nullable LivingEntity target) {
    slimeknights.tconstruct.library.tools.nbt.ProjectileAim.shoot(shooter, projectile, speed, inaccuracy, angle, target);
  }

'''+marker)
    p.write_text(s)
    p=folder/'ModifiableBowItem.java';s=p.read_text().replace('arrowItem.createArrow(level, ammo, living)', 'arrowItem.createArrow(level, ammo, living, bow)').replace('sound = SoundEvents.TRIDENT_THROW;', 'sound = SoundEvents.TRIDENT_THROW.value();');p.write_text(s)
    p=folder/'ModifiableCrossbowItem.java';s=p.read_text().replace('arrowItem.createArrow(level, ammo, living)', 'arrowItem.createArrow(level, ammo, living, living.getItemInHand(hand))')
    # Existing player shooting keeps its original angle, speed and spread; only share the math.
    start=s.index('        Vec3 upVector = living.getUpVector(1.0f);')
    end=s.index('\n\n        // add modifiers',start)
    s=s[:start]+'''        float angle = startAngle + (10 * arrowIndex);
        slimeknights.tconstruct.library.tools.nbt.ProjectileAim.shoot(living, projectile, velocity * speed, inaccuracy, angle, null);'''+s[end:]
    s=s.replace('heldStack.getItem().appendHoverText(heldStack, player.level(), nestedTooltip, tooltipFlag);', 'heldStack.getItem().appendHoverText(heldStack, net.minecraft.world.item.Item.TooltipContext.of(player.level()), nestedTooltip, tooltipFlag);')
    p.write_text(s)
    return {'files':3,'legacy_crossbow_flag_migrated':False}
