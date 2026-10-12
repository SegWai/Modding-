class MovementLabRangeSlot
{
    vector Position;
    PlayerBase Character;
    int RespawnAt = -1;
}

// Offline A/B experiment with native movement filters and vanilla animations.
class MovementLabMovementLogicMission extends MissionGameplay
{
    protected ref array<ref MovementLabRangeSlot> m_MovementLabRangeSlots = new array<ref MovementLabRangeSlot>();
    protected int m_MovementLabRangeCleanupTime = -1000;
    protected vector m_MovementLabRangeOrigin;
    protected bool m_MovementLabRangeInitialized;
    protected vector m_MovementLabRangeDirection = "0.6 0 -0.8";
    protected bool m_MovementLabAimF8Down;
    protected bool m_MovementLabHeavy = true;
    protected float m_MovementLabLastWantedGait = 2.0;
    protected bool m_MovementLabOwnsFilters;
    protected bool m_MovementLabOriginalStaminaInertia;
    protected bool m_MovementLabAnnounce = true;
    protected bool m_MovementLabWasMoving;
    protected float m_MovementLabLastSpeed;
    protected bool m_MovementLabBraking;
    protected float m_MovementLabBrakeTime;
    protected float m_MovementLabBrakeStart;
    protected float m_MovementLabBrakeTarget;
    protected float m_MovementLabBrakeDuration;
    protected float m_MovementLabBrakeSpeed;
    protected bool m_MovementLabWasTurbo;
    protected float m_MovementLabSprintExposure;
    protected float m_MovementLabBrakeStopDuration;
    protected float m_MovementLabLastAngle;
    protected float m_MovementLabBrakeAngle;
    protected int m_MovementLabLastKeys;
    protected int m_MovementLabBrakeKeys;
    protected PlayerBase m_MovementLabBrakePlayer;
    protected void MovementLabCancelStart()
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (player)
            player.MovementLabCancelStart();
    }

    protected void MovementLabCancelBrake()
    {
        // Clear only an override this mission actually started.
        if (m_MovementLabBraking && m_MovementLabBrakePlayer)
        {
            HumanInputController input = m_MovementLabBrakePlayer.GetInputController();
            if (input)
            {
                input.OverrideMovementSpeed(HumanInputControllerOverrideType.DISABLED, 0);
                input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
            }
        }
        if (m_MovementLabBrakePlayer)
            m_MovementLabBrakePlayer.MovementLabSetBrakingActive(false);
        m_MovementLabBraking = false;
        m_MovementLabBrakePlayer = null;
        m_MovementLabBrakeTime = 0;
        m_MovementLabWasMoving = false;
        m_MovementLabLastSpeed = 0;
        m_MovementLabWasTurbo = false;
        m_MovementLabSprintExposure = 0;
    }

    protected void MovementLabBeginBrake(PlayerBase player, float start, float target, float duration)
    {
        if (!m_MovementLabBraking)
        {
            m_MovementLabBrakeAngle = m_MovementLabLastAngle;
            m_MovementLabBrakeKeys = m_MovementLabLastKeys;
            // A/D-only stopping must retain the input's sideways direction,
            // rather than a possibly forward-facing current animation angle.
            if (m_MovementLabBrakeKeys == 4)
                m_MovementLabBrakeAngle = -90.0;
            else if (m_MovementLabBrakeKeys == 8)
                m_MovementLabBrakeAngle = 90.0;
            else if (m_MovementLabBrakeKeys == 2)
                m_MovementLabBrakeAngle = 180.0;
        }
        player.MovementLabSetBrakingActive(true);
        m_MovementLabBraking = true;
        m_MovementLabBrakePlayer = player;
        m_MovementLabBrakeStart = start;
        m_MovementLabBrakeSpeed = start;
        m_MovementLabBrakeTarget = target;
        m_MovementLabBrakeDuration = duration;
        m_MovementLabBrakeTime = 0;
        Print("[MovementLab Ctrl Modes v2] Braking input start=" + start + ", target=" + target + ", duration=" + duration + ", angle=" + m_MovementLabBrakeAngle);
    }

    protected void MovementLabUpdateBrake(PlayerBase player, float timeslice)
    {
        if (!m_MovementLabHeavy || !player || !player.IsAlive() || !player.GetCommand_Move() || player.IsUnconscious() || player.IsRaised() || player.IsEmotePlaying() || GetUIManager().GetMenu() || IsPaused() || timeslice > 0.25)
        {
            MovementLabCancelStart();
            MovementLabCancelBrake();
            if (player && player.IsRaised())
                player.MovementLabApplyAimWalkingSpeed();
            return;
        }
        HumanMovementState state = new HumanMovementState();
        player.GetMovementState(state);
        if (state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH)
        {
            MovementLabCancelBrake();
            player.MovementLabUpdateCrouchRules(timeslice, DayZPlayerConstants.COMMANDID_MOVE);
            return;
        }
        if (state.m_iStanceIdx != DayZPlayerConstants.STANCEIDX_ERECT)
        {
            MovementLabCancelStart();
            MovementLabCancelBrake();
            return;
        }

        // Resolve a crouch exit before interpreting held Shift/standing gait.
        player.MovementLabUpdateCrouchRules(timeslice, DayZPlayerConstants.COMMANDID_MOVE);

        // Read physical movement actions, not GetMovement during the override:
        // otherwise the generated coast could feed back and keep itself alive.
        // Direction keys are sampled independently from the generated coast.
        // Keep diagonals eligible; v4 wrongly canceled on every A/D press.
        int movementKeys = 0;
        if (GetUApi().GetInputByID(UAMoveForward).LocalValue() > 0.05)
            movementKeys = movementKeys + 1;
        if (GetUApi().GetInputByID(UAMoveBack).LocalValue() > 0.05)
            movementKeys = movementKeys + 2;
        if (GetUApi().GetInputByID(UAMoveLeft).LocalValue() > 0.05)
            movementKeys = movementKeys + 4;
        if (GetUApi().GetInputByID(UAMoveRight).LocalValue() > 0.05)
            movementKeys = movementKeys + 8;
        bool movingInput = movementKeys != 0;
        bool turbo = GetUApi().GetInputByID(UATurbo).LocalValue() > 0.05;
        if (player.MovementLabIsScrollSprinting())
            turbo = true;
        HumanInputController input = player.GetInputController();
        if (!input)
        {
            MovementLabCancelStart();
            MovementLabCancelBrake();
            return;
        }
        float wanted = player.MovementLabWantedGait();
        float previousWanted = m_MovementLabLastWantedGait;
        m_MovementLabLastWantedGait = wanted;
        if (m_MovementLabBraking && movingInput && (m_MovementLabBrakeTarget == 0 || wanted > m_MovementLabBrakeTarget))
        {
            // New movement cancels a released-input coast; a faster mode also
            // cancels a mode return. Steering alone must not restart a return.
            MovementLabCancelBrake();
            // Restore a world-owned strafe cap on this same input frame.
            player.MovementLabApplyStrafeSlow();
        }
        if (m_MovementLabBraking && movingInput && wanted < m_MovementLabBrakeTarget)
        {
            // Wheel selects a destination, not a faster braking clock.
            // Reuse the original momentum budget from the currently requested gait.
            float wheelReturnDuration = 0.42 * Math.Min(m_MovementLabBrakeSpeed / 2.0, 1.0);
            if (m_MovementLabLastKeys == 2)
                wheelReturnDuration = 0.18 * Math.Min(m_MovementLabBrakeSpeed / 2.0, 1.0);
            if (m_MovementLabBrakeSpeed > 2.05)
                wheelReturnDuration = m_MovementLabBrakeStopDuration * m_MovementLabBrakeSpeed / m_MovementLabBrakeStart;
            wheelReturnDuration = Math.Max(0.12, wheelReturnDuration);
            MovementLabBeginBrake(player, m_MovementLabBrakeSpeed, wanted, wheelReturnDuration);
        }
        if (m_MovementLabBraking && m_MovementLabBrakeTarget > 0 && !movingInput)
        {
            // Releasing all movement keys during the Shift ramp continues from the current
            // request, avoiding a jump back up to full sprint.
            float duration = Math.Max(0.18, m_MovementLabBrakeStopDuration * m_MovementLabBrakeSpeed / m_MovementLabBrakeStart);
            MovementLabBeginBrake(player, m_MovementLabBrakeSpeed, 0, duration);
        }
        if (!m_MovementLabBraking && m_MovementLabWasMoving && m_MovementLabLastSpeed > 2.05 && m_MovementLabSprintExposure > 0)
        {
            // Use the achieved gait, not the sprint command/state or a fixed 3.
            // A brief Shift tap must not get a full-sprint braking tail.
            float sprintAmount = Math.Clamp(m_MovementLabLastSpeed - 2.0, 0, 1);
            float sustained = Math.Clamp(m_MovementLabSprintExposure / 0.45, 0, 1);
            float weight = sprintAmount * sustained;
            m_MovementLabBrakeStopDuration = 0.18 + 0.97 * weight;
            if (!movingInput)
                MovementLabBeginBrake(player, m_MovementLabLastSpeed, 0, m_MovementLabBrakeStopDuration);
            else if (m_MovementLabWasTurbo && !turbo && movementKeys == m_MovementLabLastKeys)
            {
                float returnDuration = 0.12 + 0.33 * weight;
                if (player.MovementLabBaseGait() == 1.0)
                    returnDuration = m_MovementLabBrakeStopDuration;
                MovementLabBeginBrake(player, m_MovementLabLastSpeed, player.MovementLabBaseGait(), returnDuration);
            }
        }
        if (!m_MovementLabBraking && m_MovementLabWasMoving && !movingInput && m_MovementLabLastSpeed >= 1.75 && m_MovementLabLastSpeed <= 2.05)
        {
            // A small settling tail for achieved jogging, in any direction.
            // Do not require Shift, promote walking, or reuse sprint exposure.
            m_MovementLabBrakeStopDuration = 0.42 * Math.Min(m_MovementLabLastSpeed / 2.0, 1.0);
            // Backward jogging settles almost immediately: a brief walk back
            // before idle, shorter than the lateral walking tail.
            if (m_MovementLabLastKeys == 2)
                m_MovementLabBrakeStopDuration = 0.18 * Math.Min(m_MovementLabLastSpeed / 2.0, 1.0);
            MovementLabBeginBrake(player, m_MovementLabLastSpeed, 0, m_MovementLabBrakeStopDuration);
        }
        if (!m_MovementLabBraking && movingInput && wanted == 1.0 && (previousWanted > 1.0 || player.MovementLabIsModeDecreasePending()) && m_MovementLabLastSpeed > 1.05)
        {
            float modeDuration = 0.42 * Math.Min(m_MovementLabLastSpeed / 2.0, 1.0);
            if (m_MovementLabLastKeys == 2)
                modeDuration = 0.18 * Math.Min(m_MovementLabLastSpeed / 2.0, 1.0);
            m_MovementLabBrakeStopDuration = modeDuration;
            MovementLabBeginBrake(player, m_MovementLabLastSpeed, 1.0, modeDuration);
        }
        if (m_MovementLabBraking && movingInput)
        {
            // Retain the latest direction for a subsequent key-release tail.
            // During live steering it is bookkeeping only, never an override.
            m_MovementLabBrakeKeys = movementKeys;
            m_MovementLabBrakeAngle = player.GetCommand_Move().GetCurrentMovementAngle();
            if (movementKeys == 4)
                m_MovementLabBrakeAngle = -90.0;
            else if (movementKeys == 8)
                m_MovementLabBrakeAngle = 90.0;
            else if (movementKeys == 2)
                m_MovementLabBrakeAngle = 180.0;
        }
        if (!m_MovementLabBraking && movingInput)
        {
            m_MovementLabWasMoving = true;
            m_MovementLabLastKeys = movementKeys;
            m_MovementLabLastAngle = player.GetCommand_Move().GetCurrentMovementAngle();
            m_MovementLabWasTurbo = turbo;
            m_MovementLabLastSpeed = Math.Clamp(player.GetCommand_Move().GetCurrentMovementSpeed(), 0, 3);
            // A starting walk/jog request cannot count as achieved sprint just
            // because native state briefly precedes the first override frame.
            if (player.MovementLabIsStarting())
                m_MovementLabLastSpeed = Math.Min(m_MovementLabLastSpeed, player.MovementLabGetStartSpeed());
            if (turbo && m_MovementLabLastSpeed > 2.05)
                m_MovementLabSprintExposure = Math.Min(0.45, m_MovementLabSprintExposure + Math.Max(timeslice, 0));
            else
                m_MovementLabSprintExposure = 0;
            return;
        }
        m_MovementLabWasMoving = false;
        m_MovementLabWasTurbo = false;
        m_MovementLabLastSpeed = 0;
        m_MovementLabSprintExposure = 0;
        if (!m_MovementLabBraking)
            return;
        if (m_MovementLabBrakePlayer != player)
        {
            MovementLabCancelBrake();
            return;
        }
        m_MovementLabBrakeTime = m_MovementLabBrakeTime + Math.Max(timeslice, 0);
        float fraction = Math.Clamp(m_MovementLabBrakeTime / m_MovementLabBrakeDuration, 0, 1);
        if (fraction >= 1)
        {
            MovementLabCancelBrake();
            return;
        }
        // 3 = sprint, 2 = jog, 1 = walk, 0 = idle (not metres/second).
        // Let the native controller animate/collide; never move the entity directly.
        // Slow down immediately: do not linger at sprint at the start.
        // Ease toward the final gait as the remaining input approaches zero.
        // A sprint return to walking follows the SAME zero-target envelope as
        // releasing movement. Only its walking floor differs. This also covers
        // achieved sprint below 2.5, where the staged curve does not apply.
        // Ordinary Ctrl jog-to-walk and sprint-to-jog keep their existing curves.
        bool stoppingCurve = m_MovementLabBrakeTarget == 0;
        if (m_MovementLabBrakeTarget == 1.0 && m_MovementLabBrakeStart > 2.05)
            stoppingCurve = true;
        float curveTarget = m_MovementLabBrakeTarget;
        if (stoppingCurve)
            curveTarget = 0;
        float blend = 2.0 * fraction - fraction * fraction;
        if (m_MovementLabBrakeTarget == 1.0 && !stoppingCurve)
        {
            // Keep the moving jog gait briefly before entering the walk blend.
            // At the normal 0.42s budget: 0.12s jog, then 0.30s smooth blend.
            // Animation continues playing; this never freezes an animation frame.
            // Shorter backward/partial-gait budgets retain the same proportions.
            float walkFraction = Math.Clamp((fraction - 0.2857143) / 0.7142857, 0, 1);
            blend = walkFraction * walkFraction * (3.0 - 2.0 * walkFraction);
        }
        m_MovementLabBrakeSpeed = m_MovementLabBrakeStart + (curveTarget - m_MovementLabBrakeStart) * blend;
        // Redistribute an achieved near/full-sprint stop's existing time:
        // prompt sprint-to-jog, longer jog, then a short walking finish.
        // The duration/deadline and all lower-gait stops stay unchanged.
        if (m_MovementLabBrakeTarget <= 1.0 && m_MovementLabBrakeStart >= 2.5)
        {
            if (fraction < 0.18)
            {
                float sprintBlend = fraction / 0.18;
                sprintBlend = 2.0 * sprintBlend - sprintBlend * sprintBlend;
                m_MovementLabBrakeSpeed = m_MovementLabBrakeStart + (2.0 - m_MovementLabBrakeStart) * sprintBlend;
            }
            else if (fraction < 0.62)
                m_MovementLabBrakeSpeed = 2.0;
            else if (fraction < 0.82)
            {
                float jogBlend = (fraction - 0.62) / 0.20;
                jogBlend = jogBlend * jogBlend * (3.0 - 2.0 * jogBlend);
                m_MovementLabBrakeSpeed = 2.0 - jogBlend;
            }
            else if (fraction < 0.92)
                m_MovementLabBrakeSpeed = 1.0;
            else
            {
                float walkBlend = (fraction - 0.92) / 0.08;
                walkBlend = 2.0 * walkBlend - walkBlend * walkBlend;
                m_MovementLabBrakeSpeed = 1.0 - walkBlend;
            }
        }
        // Returning to walk uses the same sprint-stop phase clock, then
        // remains at walking rather than completing the idle phase.
        if (m_MovementLabBrakeTarget == 1.0)
            m_MovementLabBrakeSpeed = Math.Max(1.0, m_MovementLabBrakeSpeed);
        // During the settling portion of a pure lateral stop, request the
        // actual walk gait (1) instead of a fractional sub-walk/idle blend.
        // At the existing deadline, releasing the override allows full idle.
        if (stoppingCurve && (m_MovementLabBrakeKeys == 4 || m_MovementLabBrakeKeys == 8))
            m_MovementLabBrakeSpeed = Math.Max(1.0, m_MovementLabBrakeSpeed);
        // S-only: request the vanilla backward walk immediately for the very
        // short tail, then release to idle. Never boost a slower starting gait.
        if (stoppingCurve && m_MovementLabBrakeKeys == 2)
            m_MovementLabBrakeSpeed = Math.Min(1.0, m_MovementLabBrakeStart);
        input.OverrideMovementSpeed(HumanInputControllerOverrideType.ONE_FRAME, m_MovementLabBrakeSpeed);
        // With keys still held, native steering owns direction while speed
        // eases down. Lock an angle only for a released-input stopping tail.
        if (movingInput)
            input.OverrideMovementAngle(HumanInputControllerOverrideType.DISABLED, 0);
        else
            input.OverrideMovementAngle(HumanInputControllerOverrideType.ONE_FRAME, m_MovementLabBrakeAngle);
    }

    protected EntityAI MovementLabAddItem(EntityAI owner, string itemType)
    {
        EntityAI result = owner.GetInventory().CreateInInventory(itemType);
        if (!result)
        {
            Print("[MovementLab Loadout] Inventory placement failed for " + itemType + "; placing beside player.");
            result = EntityAI.Cast(GetGame().CreateObjectEx(itemType, owner.GetPosition(), ECE_PLACE_ON_SURFACE));
        }
        if (!result)
            Print("[MovementLab Loadout] Creation failed for " + itemType);
        return result;
    }

    protected void MovementLabFillMagazine(EntityAI owner, string magazineType)
    {
        Magazine testMagazine = Magazine.Cast(MovementLabAddItem(owner, magazineType));
        if (testMagazine)
            testMagazine.ServerSetAmmoMax();
    }

    protected void MovementLabEquipTestPlayer(PlayerBase player)
    {
        MovementLabAddItem(player, "TacticalShirt_Black");
        MovementLabAddItem(player, "CargoPants_Black");
        MovementLabAddItem(player, "MilitaryBoots_Black");
        MovementLabAddItem(player, "TacticalGloves_Black");
        MovementLabAddItem(player, "BallisticHelmet_Black");
        MovementLabAddItem(player, "BalaclavaMask_Black");
        EntityAI testVest = MovementLabAddItem(player, "PlateCarrierVest_Black");
        EntityAI testHolster;
        if (testVest)
        {
            testVest.GetInventory().CreateAttachment("PlateCarrierPouches_Black");
            testHolster = testVest.GetInventory().CreateAttachment("PlateCarrierHolster_Black");
        }
        EntityAI testPack = player.GetInventory().CreateAttachment("MovementLabTestBackpack");
        if (!testPack)
        {
            Print("[MovementLab Loadout] Custom backpack failed; using native AssaultBag_Black.");
            testPack = player.GetInventory().CreateAttachment("AssaultBag_Black");
        }
        // Backpack failure must never prevent all weapon/ammo creation.
        if (!testPack)
            testPack = player;
        Weapon_Base testRifle = Weapon_Base.Cast(testPack.GetInventory().CreateAttachment("M4A1"));
        Weapon_Base testSniper = Weapon_Base.Cast(testPack.GetInventory().CreateAttachment("SVD"));
        Weapon_Base testSmg = Weapon_Base.Cast(player.GetInventory().CreateAttachment("MP5K"));
        if (!testRifle)
            testRifle = Weapon_Base.Cast(MovementLabAddItem(player, "M4A1"));
        if (!testSniper)
            testSniper = Weapon_Base.Cast(MovementLabAddItem(player, "SVD"));
        if (!testSmg)
            testSmg = Weapon_Base.Cast(MovementLabAddItem(player, "MP5K"));
        Weapon_Base testPistol;
        if (testHolster)
            testPistol = Weapon_Base.Cast(testHolster.GetInventory().CreateAttachment("FNX45"));
        if (!testPistol)
            testPistol = Weapon_Base.Cast(MovementLabAddItem(player, "FNX45"));
        if (testRifle)
        {
            testRifle.SpawnAmmo("Mag_STANAG_30Rnd", Weapon_Base.SAMF_DEFAULT);
            testRifle.GetInventory().CreateAttachment("M4_OEBttstck");
            testRifle.GetInventory().CreateAttachment("M4_PlasticHndgrd");
            testRifle.GetInventory().CreateAttachment("M4_CarryHandleOptic");
        }
        if (testSniper)
        {
            testSniper.SpawnAmmo("Mag_SVD_10Rnd", Weapon_Base.SAMF_DEFAULT);
            testSniper.GetInventory().CreateAttachment("PSO1Optic");
        }
        if (testSmg)
            testSmg.SpawnAmmo("Mag_MP5_30Rnd", Weapon_Base.SAMF_DEFAULT);
        if (testPistol)
            testPistol.SpawnAmmo("Mag_FNX45_15Rnd", Weapon_Base.SAMF_DEFAULT);
        if (!testRifle || !testSniper || !testSmg || !testPistol)
            Print("[MovementLab Loadout] One or more weapon attachments failed; send logs.");
        // One loaded magazine plus one spare = two magazines for each weapon.
        MovementLabFillMagazine(testPack, "Mag_STANAG_30Rnd");
        MovementLabFillMagazine(testPack, "Mag_SVD_10Rnd");
        MovementLabFillMagazine(testPack, "Mag_MP5_30Rnd");
        MovementLabFillMagazine(testPack, "Mag_FNX45_15Rnd");
        array<string> testAmmoTypes = {"Ammo_556x45", "Ammo_762x54", "Ammo_9x19", "Ammo_45ACP"};
        bool testPackFull = false;
        for (int testAmmoRound = 0; testAmmoRound < 30; testAmmoRound++)
        {
            foreach (string testAmmoType: testAmmoTypes)
            {
                Magazine testAmmoStack = Magazine.Cast(testPack.GetInventory().CreateInInventory(testAmmoType));
                if (!testAmmoStack)
                {
                    testPackFull = true;
                    break;
                }
                testAmmoStack.ServerSetAmmoMax();
            }
            if (testPackFull)
                break;
        }
    }

    override void OnInit()
    {
        super.OnInit();
        MovementLabStartGate.NativeAimComparison = false;
        if (GetGame().IsMultiplayer())
            return;

        if (m_MovementLabRangeInitialized)
            return;
        m_MovementLabRangeInitialized = true;
        MovementLabStartGate.Enabled = true;
        GetGame().GetWorld().SetDate(2026, 6, 15, 12, 0);
        vector spawn = MovementLabFindPavedRange();
        spawn[1] = GetGame().SurfaceY(spawn[0], spawn[2]) + 0.2;
        PlayerBase player = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", spawn, 0, "NONE"));
        if (!player)
        {
            Print("[MovementLab] Could not create the offline character.");
            return;
        }
        MovementLabEquipTestPlayer(player);
        player.SetAllowDamage(false);
        player.GetStatWater().Set(player.GetStatWater().GetMax());
        player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
        GetGame().SelectPlayer(null, player);
        m_MovementLabRangeOrigin = spawn;
        MovementLabRemoveExtraRangeCharacters();
        for (int rangeIndex = 0; rangeIndex < 5; rangeIndex++)
        {
            MovementLabRangeSlot rangeSlot = new MovementLabRangeSlot();
            float rangeDistance = 20 + rangeIndex * 10;
            rangeSlot.Position = spawn + m_MovementLabRangeDirection * rangeDistance;
            rangeSlot.Position[1] = GetGame().SurfaceY(rangeSlot.Position[0], rangeSlot.Position[2]) + 0.2;
            m_MovementLabRangeSlots.Insert(rangeSlot);
            MovementLabSpawnRangeTarget(rangeSlot);
        }
    }

    protected bool MovementLabIsPaved(vector position)
    {
        string rangeSurface;
        GetGame().SurfaceGetType(position[0], position[2], rangeSurface);
        rangeSurface.ToLower();
        return rangeSurface.Contains("asfalt") || rangeSurface.Contains("asphalt") || rangeSurface.Contains("beton") || rangeSurface.Contains("concrete") || rangeSurface.Contains("runway");
    }

    protected vector MovementLabFindPavedRange()
    {
        vector rangeAnchor = "4500 0 10300";
        // Search nearby airfield pavement; check the entire line, not only player spawn.
        for (int rangeRadius = 0; rangeRadius <= 300; rangeRadius += 20)
        {
            for (int rangeX = -rangeRadius; rangeX <= rangeRadius; rangeX += 20)
            {
                for (int rangeZ = -rangeRadius; rangeZ <= rangeRadius; rangeZ += 20)
                {
                    if (Math.AbsInt(rangeX) != rangeRadius && Math.AbsInt(rangeZ) != rangeRadius)
                        continue;
                    vector rangeCandidate = rangeAnchor;
                    rangeCandidate[0] = rangeCandidate[0] + rangeX;
                    rangeCandidate[2] = rangeCandidate[2] + rangeZ;
                    bool rangePaved = true;
                    for (float rangeSample = 0; rangeSample <= 60; rangeSample += 5)
                    {
                        vector rangePoint = rangeCandidate + m_MovementLabRangeDirection * rangeSample;
                        if (!MovementLabIsPaved(rangePoint))
                        {
                            rangePaved = false;
                            break;
                        }
                    }
                    if (rangePaved)
                    {
                        Print("[MovementLab Range] Verified paved60m line at " + rangeCandidate);
                        return rangeCandidate;
                    }
                }
            }
        }
        Print("[MovementLab Range] Pavement search failed; send logs with spawn location.");
        return rangeAnchor;
    }

    protected void MovementLabRemoveExtraRangeCharacters()
    {
        if (GetGame().IsMultiplayer())
            return;
        array<Object> rangeObjects = new array<Object>();
        array<CargoBase> rangeCargos = new array<CargoBase>();
        GetGame().GetObjectsAtPosition3D(m_MovementLabRangeOrigin, 100, rangeObjects, rangeCargos);
        foreach (Object rangeObject: rangeObjects)
        {
            PlayerBase rangePerson = PlayerBase.Cast(rangeObject);
            if (!rangePerson || rangePerson == GetGame().GetPlayer())
                continue;
            bool rangeKeep = false;
            foreach (MovementLabRangeSlot retainedSlot: m_MovementLabRangeSlots)
            {
                if (retainedSlot.Character == rangePerson)
                {
                    rangeKeep = true;
                    break;
                }
            }
            if (!rangeKeep)
                GetGame().ObjectDelete(rangePerson);
        }
    }

    protected void MovementLabSpawnRangeTarget(MovementLabRangeSlot slot)
    {
        // Never spawn over an existing live target in this slot.
        if (slot.Character && slot.Character.IsAlive())
            return;
        slot.Character = PlayerBase.Cast(GetGame().CreatePlayer(null, "SurvivorM_Mirek", slot.Position, 0, "NONE"));
        slot.RespawnAt = -1;
        if (!slot.Character)
        {
            slot.RespawnAt = GetGame().GetTime() + 3000;
            Print("[MovementLab Range] Target creation failed; retrying.");
            return;
        }
        slot.Character.MovementLabSetRangeTarget();
        slot.Character.SetOrientation("180 0 0");
        MovementLabAddItem(slot.Character, "TacticalShirt_Black");
        MovementLabAddItem(slot.Character, "CargoPants_Black");
        MovementLabAddItem(slot.Character, "MilitaryBoots_Black");
        slot.Character.GetStatWater().Set(slot.Character.GetStatWater().GetMax());
        slot.Character.GetStatEnergy().Set(slot.Character.GetStatEnergy().GetMax());
    }

    protected void MovementLabUpdateRangeTargets()
    {
        foreach (MovementLabRangeSlot targetSlot: m_MovementLabRangeSlots)
        {
            if (targetSlot.Character && targetSlot.Character.IsAlive())
                continue;
            if (targetSlot.RespawnAt < 0)
                targetSlot.RespawnAt = GetGame().GetTime() + 3000;
            if (GetGame().GetTime() < targetSlot.RespawnAt)
                continue;
            if (targetSlot.Character)
                GetGame().ObjectDelete(targetSlot.Character);
            MovementLabSpawnRangeTarget(targetSlot);
        }
    }

    // PlayerBase normally reapplies three stamina modifiers each command tick.
    // Take over those modifiers for this mission, preserving the same formula.
    protected void MovementLabApplyFilters(PlayerBase player, bool heavy)
    {
        HumanCommandMove move = player.GetCommand_Move();
        if (!move)
            return;

        float sprintInertia = 1.0;
        float runSprint = 1.0;
        if (m_MovementLabOriginalStaminaInertia && player.GetStaminaHandler())
        {
            sprintInertia = 2.0 - player.GetStaminaHandler().GetSyncedStaminaNormalized();
            runSprint = sprintInertia * 0.5;
        }

        float direction = 1.0;
        float turn = 1.0;
        float sprintDirection = sprintInertia;
        float sprintTurn = sprintInertia;
        if (heavy)
        {
            runSprint = runSprint * 4.0;
            direction = 2.5;
            sprintDirection = sprintDirection * 2.0;
            turn = 1.6; // Keep the preferred responsive body rotation permanently.
            sprintTurn = sprintTurn * 2.5;

        }
        // Preserve startup filters, but do not let their long sprint span
        // fight the braking request after the user has released Shift/W.
        if (m_MovementLabBraking)
            runSprint = 0.35;
        move.SetRunSprintFilterModifier(runSprint);
        move.SetDirectionFilterModifier(direction);
        move.SetDirectionSprintFilterModifier(sprintDirection);
        move.SetTurnSpanModifier(turn);
        move.SetTurnSpanSprintModifier(sprintTurn);
    }

    override void OnUpdate(float timeslice)
    {
        // Read transient wheel input every rendered frame, before native UI processing.
        PlayerBase wheelFramePlayer = PlayerBase.Cast(GetGame().GetPlayer());
        if (wheelFramePlayer)
            wheelFramePlayer.MovementLabCaptureWheelTarget();
        super.OnUpdate(timeslice);
        if (GetGame().IsMultiplayer())
            return;
        MovementLabUpdateRangeTargets();
        if (GetGame().GetTime() - m_MovementLabRangeCleanupTime >= 1000)
        {
            m_MovementLabRangeCleanupTime = GetGame().GetTime();
            MovementLabRemoveExtraRangeCharacters();
        }
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        MovementLabUpdateBrake(player, timeslice);
        if (!player || !player.IsAlive() || !player.GetCommand_Move())
            return;
        if (!m_MovementLabOwnsFilters)
        {
            m_MovementLabOriginalStaminaInertia = CfgGameplayHandler.GetAllowStaminaAffectInertia();
            CfgGameplayHandler.m_Data.PlayerData.MovementData.allowStaminaAffectInertia = false;
            m_MovementLabOwnsFilters = true;
        }
        MovementLabApplyFilters(player, m_MovementLabHeavy);
        if (m_MovementLabAnnounce)
        {
            string mode = "VANILLA FILTERS";
            if (m_MovementLabHeavy)
                mode = "CTRL WALK/JOG + HOLD SHIFT SPRINT";
            string message = "[MovementLab Ctrl Modes v10] " + mode + " - Responsive body turning enabled. F7 compares vanilla. Ctrl toggles jog/walk; hold Shift to sprint.";
            player.MessageStatus(message);
            Print(message);
            m_MovementLabAnnounce = false;
        }
    }

    override void OnKeyPress(int key)
    {
        super.OnKeyPress(key);
        if (key == KeyCode.KC_F8 && !m_MovementLabAimF8Down)
        {
            m_MovementLabAimF8Down = true;
            if (!GetGame().IsMultiplayer() && GetGame().GetInput().HasGameFocus() && !GetGame().GetUIManager().GetMenu())
            {
                MovementLabStartGate.NativeAimComparison = !MovementLabStartGate.NativeAimComparison;
                Print("[MovementLab Aim Comparison] Native standing aim=" + MovementLabStartGate.NativeAimComparison);
            }
        }

        if (key == KeyCode.KC_F7 && !GetGame().IsMultiplayer())
        {
            m_MovementLabHeavy = !m_MovementLabHeavy;
            MovementLabStartGate.Enabled = m_MovementLabHeavy;
            MovementLabCancelStart();
            MovementLabCancelBrake();
            m_MovementLabAnnounce = true;
        }
    }

    override void OnKeyRelease(int key)
    {
        super.OnKeyRelease(key);
        if (key == KeyCode.KC_F8)
            m_MovementLabAimF8Down = false;
    }

    override void OnMissionFinish()
    {
        foreach (MovementLabRangeSlot finishSlot: m_MovementLabRangeSlots)
        {
            if (finishSlot.Character)
                GetGame().ObjectDelete(finishSlot.Character);
        }
        m_MovementLabRangeSlots.Clear();
        MovementLabStartGate.Enabled = false;
        MovementLabStartGate.NativeAimComparison = false;
        MovementLabCancelStart();
        MovementLabCancelBrake();
        if (m_MovementLabOwnsFilters)
        {
            PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
            if (player)
                MovementLabApplyFilters(player, false);
            CfgGameplayHandler.m_Data.PlayerData.MovementData.allowStaminaAffectInertia = m_MovementLabOriginalStaminaInertia;
            m_MovementLabOwnsFilters = false;
        }
        super.OnMissionFinish();
    }
}

Mission CreateCustomMission(string path)
{
    return new MovementLabMovementLogicMission();
}
