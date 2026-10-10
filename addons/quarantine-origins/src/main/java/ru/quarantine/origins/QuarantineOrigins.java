package ru.quarantine.origins;

import com.cyberday1.neoorigins.attachment.OriginAttachments;
import com.Harbinger.Spore.core.Seffects;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.tick.PlayerTickEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;

@Mod("quarantine_origins")
public final class QuarantineOrigins {
    private static final ResourceLocation INFECTED=ResourceLocation.parse("quarantine:infected");
    public QuarantineOrigins() {
        NeoForge.EVENT_BUS.addListener(this::onTick);
        NeoForge.EVENT_BUS.addListener(this::onTarget);
    }
    public static boolean isInfected(Player player) {
        return player.getData(OriginAttachments.originData()).getOrigins().containsValue(INFECTED);
    }
    private void onTick(PlayerTickEvent.Post event) {
        if (!(event.getEntity() instanceof ServerPlayer p) || p.tickCount%20!=0) return;
        if (!isInfected(p) || p.isCreative() || p.isSpectator()) {
            p.getPersistentData().remove("quarantine_cold_seconds"); return;
        }
        // Short lease expires after class change, without deleting armor-granted Symbiosis.
        if (!p.hasEffect(Seffects.SYMBIOSIS) || p.getEffect(Seffects.SYMBIOSIS).getDuration()<40)
            p.addEffect(new MobEffectInstance(Seffects.SYMBIOSIS,60,0,true,false,true));
        boolean cold=p.isInPowderSnow || (p.level().getBiome(p.blockPosition()).value().getBaseTemperature()<0.15F
                && (p.level().canSeeSky(p.blockPosition()) || p.isInWater()));
        cold=cold && !p.hasEffect(MobEffects.FIRE_RESISTANCE);
        int seconds=cold?Math.min(10,p.getPersistentData().getInt("quarantine_cold_seconds")+1):0;
        p.getPersistentData().putInt("quarantine_cold_seconds",seconds);
        if (seconds>=10 && !p.hasEffect(Seffects.FROSTBITE))
            p.addEffect(new MobEffectInstance(Seffects.FROSTBITE,60,0,false,true,true));
        if (p.hasEffect(Seffects.FROSTBITE)) {
            p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,40,0,false,false,true));
            if (p.tickCount%80==0) p.hurt(p.damageSources().freeze(),2.0F+Math.min(4,p.getEffect(Seffects.FROSTBITE).getAmplifier()));
        }
    }
    private void onTarget(LivingChangeTargetEvent event) {
        if (!(event.getEntity() instanceof Mob mob) || !(event.getNewAboutToBeSetTarget() instanceof ServerPlayer p)) return;
        if (!isInfected(p) || p.hasEffect(Seffects.FROSTBITE) || mob.getTarget()==p || mob.distanceToSqr(p)<=64) return;
        var id=BuiltInRegistries.ENTITY_TYPE.getKey(mob.getType());
        // Basic infected only: elites, evolved monsters, calamities and other mods keep their own AI.
        if (!id.getNamespace().equals("spore") || !id.getPath().startsWith("inf_") || mob.getMaxHealth()>80) return;
        if (mob.getLastHurtByMob()==p && mob.tickCount-mob.getLastHurtByMobTimestamp()<600) return;
        event.setNewAboutToBeSetTarget(null);
    }
}
