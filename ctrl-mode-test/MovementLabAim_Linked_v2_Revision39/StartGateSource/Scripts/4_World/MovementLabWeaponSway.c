// Suppress procedural weapon sway in the offline test, without changing recoil
// or the gun/hand animation graph. Raised hip fire, ironsights and optics share
// the native aiming model. Leaning does not bypass these hooks.
class MovementLabWeaponSway
{
    static bool ShouldSuppress(PlayerBase player)
    {
        if (!MovementLabStartGate.Enabled || !GetGame() || GetGame().IsMultiplayer())
            return false;
        if (!player || GetGame().GetPlayer() != player || !player.IsAlive() || player.IsUnconscious() || !player.IsRaised())
            return false;
        EntityAI held = player.GetItemInHands();
        return held && held.IsWeapon();
    }
}

modded class DayZPlayerImplementAiming
{
    override protected void ApplyBreathingPattern(out float x_axis, out float y_axis, float pAmplitude, float pTotalTime, float weight)
    {
        super.ApplyBreathingPattern(x_axis, y_axis, pAmplitude, pTotalTime, weight);
        if (MovementLabWeaponSway.ShouldSuppress(m_PlayerPb))
        {
            x_axis = 0;
            y_axis = 0;
        }
    }

    override protected void ApplyHorizontalNoise(out float x_axis, out float y_axis, float smooth_time, float max_velocity_low, float max_velocity_high, float velocity_modifier, float max_distance, float weight, float pDt)
    {
        super.ApplyHorizontalNoise(x_axis, y_axis, smooth_time, max_velocity_low, max_velocity_high, velocity_modifier, max_distance, weight, pDt);
        if (MovementLabWeaponSway.ShouldSuppress(m_PlayerPb))
        {
            x_axis = 0;
            y_axis = 0;
        }
    }
}

modded class DayZPlayerCameraIronsights
{
    override void OnUpdate(float pDt, out DayZPlayerCameraResult pOutResult)
    {
        bool movementLabStableSight = MovementLabWeaponSway.ShouldSuppress(PlayerBase.Cast(m_pPlayer));
        float movementLabOriginalDynamics = m_dynamicsStrength;
        if (movementLabStableSight)
        {
            // Native sight misalignment uses aim delta and movement bob with
            // this strength. Clear previous filter velocity as well.
            m_dynamicsStrength = 0;
            m_velocityYaw[0] = 0;
            m_velocityPitch[0] = 0;
        }
        super.OnUpdate(pDt, pOutResult);
        m_dynamicsStrength = movementLabOriginalDynamics;
    }
}
