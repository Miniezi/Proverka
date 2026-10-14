"""Migrate the shared durability callbacks across tools, armor and launchers."""
def migrate(root):
    source=root/'src/main/java/slimeknights/tconstruct/library/tools'
    names=['item/ModifiableItem.java','item/armor/ModifiableArmorItem.java','item/ranged/ModifiableLauncherItem.java']
    for name in names:
        p=source/name;s=p.read_text()
        s=s.replace('boolean canBeDepleted()', 'boolean isDamageable(ItemStack stack)')
        s=s.replace('canBeDepleted()', 'isDamageable(stack)')
        s=s.replace('Consumer<T> onBroken', 'Consumer<net.minecraft.world.item.Item> onBroken')
        s=s.replace('onBroken.accept(damager);', 'onBroken.accept(stack.getItem());')
        s=s.replace('public void appendHoverText(ItemStack stack, @Nullable Level level,',
                    'public void appendHoverText(ItemStack stack, net.minecraft.world.item.Item.TooltipContext context,')
        s=s.replace('TooltipUtil.addInformation(this, stack, level, tooltip,',
                    'TooltipUtil.addInformation(this, stack, context.level(), tooltip,')
        p.write_text(s)
    p=source/'helper/ToolDamageUtil.java';s=p.read_text()
    s=s.replace('Consumer<T> onBroken', 'Consumer<net.minecraft.world.item.Item> onBroken')
    s=s.replace('onBroken.accept(damager);', 'onBroken.accept(stack.getItem());')
    s=s.replace('stack.getItem().canBeDepleted()', 'stack.getItem().isDamageable(stack)')
    s=s.replace('stack.getOrCreateTag().putBoolean(ToolStack.TAG_BROKEN, true);',
                'slimeknights.tconstruct.library.tools.nbt.ItemStackData.update(stack, data -> data.putBoolean(ToolStack.TAG_BROKEN, true));')
    s=s.replace('stack.getTag()', 'slimeknights.tconstruct.library.tools.nbt.ItemStackData.read(stack)')
    s=s.replace('entity.broadcastBreakEvent(slot);', 'entity.onEquippedItemBroken(entity.getItemBySlot(slot).getItem(), slot);')
    s=s.replace('entity.broadcastBreakEvent(hand);', 'entity.onEquippedItemBroken(entity.getItemInHand(hand).getItem(), hand == InteractionHand.MAIN_HAND ? EquipmentSlot.MAINHAND : EquipmentSlot.OFFHAND);')
    p.write_text(s)
    return {'files':4,'full_toolstack_damage_validated':False}
