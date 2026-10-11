modded class ModItemRegisterCallbacks
{
    override void RegisterEmptyHanded(DayZPlayerType pType, DayzPlayerItemBehaviorCfg pBehavior)
    {
        super.RegisterEmptyHanded(pType, pBehavior);
        pType.SetDefaultItemInHandsProfile("MovementLabSlowCrouchClips/SlowCrouch.asi", pBehavior);
        Print("[MovementLab] Isolated slow-crouch profile registered for empty hands.");
    }
}
