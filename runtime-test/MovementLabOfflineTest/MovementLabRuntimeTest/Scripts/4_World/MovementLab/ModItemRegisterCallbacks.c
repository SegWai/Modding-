modded class ModItemRegisterCallbacks
{
    override void RegisterEmptyHanded(DayZPlayerType pType, DayzPlayerItemBehaviorCfg pBehavior)
    {
        super.RegisterEmptyHanded(pType, pBehavior);
        pType.SetDefaultItemInHandsProfile("MovementLabRuntimeTest/Animations/MovementLab_ArmLift_Greeting.asi", pBehavior);
        Print("[MovementLab] Registered the arm-lift greeting profile for empty hands.");
    }
}
