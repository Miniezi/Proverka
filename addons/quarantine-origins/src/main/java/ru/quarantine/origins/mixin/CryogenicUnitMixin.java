package ru.quarantine.origins.mixin;

import com.Harbinger.Spore.SBlockEntities.CDUBlockEntity;
import com.Harbinger.Spore.core.SConfig;
import com.Harbinger.Spore.core.Seffects;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import ru.quarantine.origins.QuarantineOrigins;

@Mixin(value=CDUBlockEntity.class,remap=false)
public abstract class CryogenicUnitMixin {
    @Inject(method="cleanInfection",at=@At("TAIL"),remap=false)
    private void quarantine$freezeInfected(BlockPos pos, CallbackInfo ci) {
        BlockEntity block=(BlockEntity)(Object)this;
        if (block.getLevel()==null || block.getLevel().isClientSide()) return;
        double diameter=2.0*SConfig.DATAGEN.cryo_range.get();
        AABB area=AABB.ofSize(new Vec3(pos.getX(),pos.getY(),pos.getZ()),diameter,diameter,diameter);
        for (ServerPlayer p:block.getLevel().getEntitiesOfClass(ServerPlayer.class,area)) {
            if (!QuarantineOrigins.isInfected(p) || p.isCreative() || p.isSpectator()) continue;
            boolean alreadyHandled=false;
            for (var armor:p.getArmorSlots()) if (armor.is(CDUBlockEntity.fungalItems)) { alreadyHandled=true; break; }
            if (alreadyHandled) continue;
            var previous=p.getEffect(Seffects.FROSTBITE);
            int amplifier=previous==null?0:Math.min(4,previous.getAmplifier()+1);
            p.addEffect(new MobEffectInstance(Seffects.FROSTBITE,600,amplifier));
        }
    }
}
