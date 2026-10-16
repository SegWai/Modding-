// Change only the native turn-in-place trigger; keep native turn execution.
modded class DayZPlayerTypeUtils
{
    override static void DayZPlayerTypeInitMovement(DayZPlayerType pType)
    {
        super.DayZPlayerTypeInitMovement(pType);
        SHumanCommandMoveSettings movementSettings = pType.CommandMoveSettingsW();
        if (movementSettings)
        {
            // This native setting is in degrees, not radians.
            movementSettings.m_fTurnAngle = 90;
            Print("[MovementLab turn v77] Native turn-in-place threshold=90 degrees left/right.");
        }
    }
}
