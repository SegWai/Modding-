// Offline A/B experiment with native movement filters and vanilla animations.
class MovementLabMovementLogicMission extends MissionGameplay
{
    protected bool m_MovementLabRangeInitialized;
    protected ref MovementLabInfectedRange m_MovementLabInfectedRange;
    protected int m_MovementLabGrenadeNextCheck;
    protected bool m_MovementLabGrenadeSpaceWarning;
    protected PlayerBase m_MovementLabMaleTarget;
    protected PlayerBase m_MovementLabFemaleTarget;
    protected int m_MovementLabMaleRespawnAt;
    protected vector m_MovementLabMaleDeathPosition;
    protected vector m_MovementLabMaleDeathOrientation;
    protected ref array<string> m_MovementLabAK103MagazineClasses = new array<string>();
    protected ref array<string> m_MovementLabAK103CheckedWeapons = new array<string>();
    protected int m_MovementLabAK103NextCheck;
    protected vector m_MovementLabRangeDirection = "0.6 0 -0.8";
    protected bool m_MovementLabRightADSDown;
    protected bool m_MovementLabRightADSEligible;
    protected int m_MovementLabRightADSTime;
    protected bool m_MovementLabViewmodelF9Down;
    protected bool m_MovementLabViewmodelF10Down;
    protected bool m_MovementLabAltDown;
    protected int m_MovementLabAltTime;
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
        if (target == 1.0)
            duration = 1.5;
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
        bool turbo = player.MovementLabIsScrollSprinting();
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
        float curveTarget = m_MovementLabBrakeTarget;
        if (stoppingCurve)
            curveTarget = 0;
        float blend = 2.0 * fraction - fraction * fraction;
        if (m_MovementLabBrakeTarget == 1.0)
            blend = fraction * fraction * (3.0 - 2.0 * fraction);
        m_MovementLabBrakeSpeed = m_MovementLabBrakeStart + (curveTarget - m_MovementLabBrakeStart) * blend;
        // Redistribute an achieved near/full-sprint stop's existing time:
        // prompt sprint-to-jog, longer jog, then a short walking finish.
        // The duration/deadline and all lower-gait stops stay unchanged.
        if (m_MovementLabBrakeTarget == 0 && m_MovementLabBrakeStart >= 2.5)
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

    protected void MovementLabGiveAllAK103Magazines(PlayerBase player)
    {
        if (!player || !player.IsAlive())
            return;
        int now = GetGame().GetTime();
        if (now < m_MovementLabAK103NextCheck)
            return;
        m_MovementLabAK103NextCheck = now + 500;
        EntityAI held = player.GetEntityInHands();
        if (!held || !held.IsWeapon())
            return;
        string identifier = held.GetType() + " " + held.GetDisplayName();
        identifier.ToLower();
        identifier.Replace("-", "");
        identifier.Replace("_", "");
        identifier.Replace(" ", "");
        if (!identifier.Contains("ak103"))
            return;
        if (m_MovementLabAK103CheckedWeapons.Find(held.GetType()) >= 0)
            return;
        m_MovementLabAK103CheckedWeapons.Insert(held.GetType());
        TStringArray compatibleMagazines = new TStringArray();
        GetGame().ConfigGetTextArray("CfgWeapons " + held.GetType() + " magazines", compatibleMagazines);
        EntityAI destination = player.FindAttachmentBySlotName("Back");
        if (!destination)
            destination = player;
        foreach (string magazineClass: compatibleMagazines)
        {
            if (m_MovementLabAK103MagazineClasses.Find(magazineClass) >= 0)
                continue;
            if (GetGame().ConfigGetInt("CfgMagazines " + magazineClass + " count") <= 0)
                continue;
            Magazine magazine = Magazine.Cast(MovementLabAddItem(destination, magazineClass));
            if (!magazine)
                continue;
            magazine.ServerSetAmmoMax();
            m_MovementLabAK103MagazineClasses.Insert(magazineClass);
            Print("[MovementLab AK103 magazines] " + held.GetType() + " compatible=" + magazineClass);
        }
    }

    protected void MovementLabFillMagazine(EntityAI owner, string magazineType)
    {
        Magazine testMagazine = Magazine.Cast(MovementLabAddItem(owner, magazineType));
        if (testMagazine)
            testMagazine.ServerSetAmmoMax();
    }

    protected void MovementLabEquipNativeFallback(PlayerBase player)
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
        // Reserve grenades before weapons and ten-magazine batches fill cargo.
        MovementLabRefillGrenades(player);
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
        // Ten full spare magazines per weapon. No loose ammunition is spawned.
        for (int spareIndex = 0; spareIndex < 10; spareIndex++)
        {
            MovementLabFillMagazine(testPack, "Mag_STANAG_30Rnd");
            MovementLabFillMagazine(testPack, "Mag_SVD_10Rnd");
            MovementLabFillMagazine(testPack, "Mag_MP5_30Rnd");
            MovementLabFillMagazine(testPack, "Mag_FNX45_15Rnd");
        }

    }

    protected bool MovementLabNameContains(string text, array<string> terms)
    {
        text.ToLower();
        foreach (string term: terms)
        {
            if (text.IndexOf(term) >= 0)
                return true;
        }
        return false;
    }

    protected string MovementLabFindSnafuWeapon(string role)
    {
        array<string> terms;
        string fallbackPistol;
        if (role == "sniper308")
            terms = {"m24", "m40", "m700", "remington", "t5000", "l96", "awm", "awp", "sr25", "m110", "rsass", "sniper"};
        if (role == "rifle")
            terms = {"m4", "hk416", "scar", "ak", "ar15", "rifle"};
        if (role == "sniper")
            terms = {"m24"};
        if (role == "smg")
            terms = {"mp5", "mp7", "mp9", "ump", "kriss", "vector", "mpx"};
        int configCount = GetGame().ConfigGetChildrenCount("CfgWeapons");
        for (int configIndex = 0; configIndex < configCount; configIndex++)
        {
            string candidate;
            GetGame().ConfigGetChildName("CfgWeapons", configIndex, candidate);
            string path = "CfgWeapons " + candidate;
            if (GetGame().ConfigGetInt(path + " scope") != 2)
                continue;
            string label;
            GetGame().ConfigGetText(path + " displayName", label);
            string identity = candidate + " " + label;
            identity.ToLower();
            if (identity.IndexOf("snafu") < 0)
                continue;
            array<string> compatibleMags = new array<string>();
            GetGame().ConfigGetTextArray(path + " magazines", compatibleMags);
            if (compatibleMags.Count() == 0)
                continue;
            bool pistol = GetGame().IsKindOf(candidate, "Pistol_Base");
            if (role == "pistol" && pistol)
            {
                if (identity.Contains("glock") || identity.Contains("g19") || identity.Contains("g17") || identity.Contains("g18"))
                    return candidate;
                if (fallbackPistol == "")
                    fallbackPistol = candidate;
                continue;
            }
            if (role == "smg" && identity.Contains("p90"))
                continue;
            if (role == "sniper308" && !MovementLabWeaponIs308(candidate))
                continue;
            if (role != "pistol" && !pistol && MovementLabNameContains(identity, terms))
                return candidate;
        }
        if (role == "pistol" && GetGame().ConfigGetInt("CfgWeapons Glock19 scope") == 2)
            return "Glock19";
        if (role == "pistol" && fallbackPistol != "")
            return fallbackPistol;
        Print("[MovementLab SNAFU] No supported " + role + " found in loaded CfgWeapons.");
        return "";
    }

    protected void MovementLabAddSnafuWeapon(PlayerBase player, EntityAI backpack, string role)
    {
        string weaponClass = MovementLabFindSnafuWeapon(role);
        if (weaponClass == "")
            return;
        Weapon_Base weapon;
        if (role == "rifle" || role == "sniper" || role == "sniper308")
            weapon = Weapon_Base.Cast(backpack.GetInventory().CreateAttachment(weaponClass));
        if (!weapon)
            weapon = Weapon_Base.Cast(MovementLabAddItem(player, weaponClass));
        if (!weapon)
            return;
        array<string> magazines = new array<string>();
        GetGame().ConfigGetTextArray("CfgWeapons " + weaponClass + " magazines", magazines);
        string magazineClass;
        foreach (string compatible: magazines)
        {
            if (GetGame().ConfigGetInt("CfgMagazines " + compatible + " count") > 0)
            {
                magazineClass = compatible;
                break;
            }
        }
        if (magazineClass == "")
        {
            Print("[MovementLab SNAFU] No detachable magazine config for " + weaponClass);
            return;
        }
        weapon.SpawnAmmo(magazineClass, Weapon_Base.SAMF_DEFAULT);
        for (int snafuSpareIndex = 0; snafuSpareIndex < 10; snafuSpareIndex++)
            MovementLabFillMagazine(backpack, magazineClass);
        // Modular guns may require parts. Select compatible public parts by their
        // declared inventory slots; never attach an incompatible native M4 part.
        array<string> attachmentSlots = new array<string>();
        GetGame().ConfigGetTextArray("CfgWeapons " + weaponClass + " attachments", attachmentSlots);
        foreach (string attachmentSlot: attachmentSlots)
        {
            string slotKey = attachmentSlot;
            slotKey.ToLower();
            if (slotKey.IndexOf("handguard") < 0 && slotKey.IndexOf("buttstock") < 0 && slotKey.IndexOf("receiver") < 0)
                continue;
            int partCount = GetGame().ConfigGetChildrenCount("CfgVehicles");
            for (int partIndex = 0; partIndex < partCount; partIndex++)
            {
                string partClass;
                GetGame().ConfigGetChildName("CfgVehicles", partIndex, partClass);
                string partPath = "CfgVehicles " + partClass;
                if (GetGame().ConfigGetInt(partPath + " scope") != 2)
                    continue;
                array<string> partSlots = new array<string>();
                GetGame().ConfigGetTextArray(partPath + " inventorySlot", partSlots);
                if (partSlots.Find(attachmentSlot) < 0)
                    continue;
                EntityAI part = weapon.GetInventory().CreateAttachment(partClass);
                if (part)
                    break;
            }
        }
        bool longRange = role == "sniper" || role == "sniper308";
        MovementLabEquipFullAttachments(weapon, longRange, 0);
        Print("[MovementLab SNAFU] " + role + "=" + weaponClass + " magazine=" + magazineClass + " ten full spares");
    }

    protected bool MovementLabWeaponIs308(string weaponClass)
    {
        TStringArray allowedAmmo = new TStringArray();
        GetGame().ConfigGetTextArray("CfgWeapons " + weaponClass + " chamberableFrom", allowedAmmo);
        foreach (string ammoClass: allowedAmmo)
        {
            string caliber = ammoClass;
            caliber.ToLower();
            if (caliber.Contains("308") || caliber.Contains("762x51") || caliber.Contains("7.62x51"))
                return true;
        }
        return false;
    }

    protected bool MovementLabBottleSuppressor(string partClass)
    {
        string identity = partClass;
        identity.ToLower();
        return GetGame().IsKindOf(partClass, "ImprovisedSuppressor") || identity.Contains("bottle") || identity.Contains("improvis");
    }

    protected bool MovementLabRealSuppressor(string partClass)
    {
        if (MovementLabBottleSuppressor(partClass))
            return false;
        string identity = partClass;
        identity.ToLower();
        return GetGame().IsKindOf(partClass, "SuppressorBase") || identity.Contains("suppress") || identity.Contains("silenc");
    }

    protected bool MovementLabPreferredAttachment(string identity, string slotKey, bool longRange)
    {
        identity.ToLower();
        if (slotKey.Contains("optic") || slotKey.Contains("scope"))
        {
            if (longRange)
                return identity.Contains("scope") || identity.Contains("sniper") || identity.Contains("hunting") || identity.Contains("pso") || identity.Contains("atacr") || identity.Contains("nightforce");
            return identity.Contains("reflex") || identity.Contains("red") || identity.Contains("kobra") || identity.Contains("acog") || identity.Contains("rds");
        }
        if (slotKey.Contains("suppress") || slotKey.Contains("muzzle"))
            return MovementLabRealSuppressor(identity);
        return identity.Contains("snafu");
    }

    protected void MovementLabEquipFullAttachments(EntityAI target, bool longRange, int depth)
    {
        if (!target || depth >= 3)
            return;
        int availableSlots = target.GetInventory().GetAttachmentSlotsCount();
        int partCount = GetGame().ConfigGetChildrenCount("CfgVehicles");
        for (int attachmentIndex = 0; attachmentIndex < availableSlots; attachmentIndex++)
        {
            int attachmentId = target.GetInventory().GetAttachmentSlotId(attachmentIndex);
            if (target.GetInventory().FindAttachment(attachmentId))
                continue;
            string attachmentName = InventorySlots.GetSlotName(attachmentId);
            string slotKey = attachmentName;
            slotKey.ToLower();
            if (slotKey.Contains("magazine") || slotKey.Contains("ghillie") || slotKey.Contains("wrap"))
                continue;
            bool suppressorSlot = slotKey.Contains("suppress") || slotKey.Contains("silenc") || slotKey.Contains("muzzle");
            bool fitted = false;
            for (int preferencePass = 0; preferencePass < 2; preferencePass++)
            {
                if (fitted)
                    break;
                for (int partIndex = 0; partIndex < partCount; partIndex++)
                {
                    string partClass;
                    GetGame().ConfigGetChildName("CfgVehicles", partIndex, partClass);
                    string partPath = "CfgVehicles " + partClass;
                    if (GetGame().ConfigGetInt(partPath + " scope") != 2)
                        continue;
                    TStringArray partSlots = new TStringArray();
                    GetGame().ConfigGetTextArray(partPath + " inventorySlot", partSlots);
                    if (partSlots.Find(attachmentName) < 0)
                        continue;
                    // Never equip bottle/improvised suppressors, including on fallback passes.
                    if (MovementLabBottleSuppressor(partClass))
                        continue;
                    // Search every compatible real suppressor before accepting another muzzle part.
                    if (suppressorSlot && preferencePass == 0 && !MovementLabRealSuppressor(partClass))
                        continue;
                    if (!suppressorSlot && preferencePass == 0 && !MovementLabPreferredAttachment(partClass, slotKey, longRange))
                        continue;
                    EntityAI part = target.GetInventory().CreateAttachmentEx(partClass, attachmentId);
                    if (!part)
                        continue;
                    if (part.GetCompEM())
                        part.GetCompEM().SetEnergy(part.GetCompEM().GetEnergyMax());
                    fitted = true;
                    Print("[MovementLab Full Attachments] " + target.GetType() + " slot=" + attachmentName + " part=" + partClass);
                    break;
                }
            }
            if (!fitted)
                Print("[MovementLab Full Attachments] No accepted part for " + target.GetType() + " slot=" + attachmentName);
        }
        for (int childIndex = 0; childIndex < target.GetInventory().AttachmentCount(); childIndex++)
        {
            EntityAI child = target.GetInventory().GetAttachmentFromIndex(childIndex);
            if (child && !Magazine.Cast(child))
                MovementLabEquipFullAttachments(child, longRange, depth + 1);
        }
    }

    protected void MovementLabEquipMMGClothing(PlayerBase player, string slotName, string fallbackClass)
    {
        int clothingCount = GetGame().ConfigGetChildrenCount("CfgVehicles");
        int slotId = InventorySlots.GetSlotIdFromString(slotName);
        for (int pass = 0; pass < 2; pass++)
        {
            for (int clothingIndex = 0; clothingIndex < clothingCount; clothingIndex++)
            {
                string clothingClass;
                GetGame().ConfigGetChildName("CfgVehicles", clothingIndex, clothingClass);
                string path = "CfgVehicles " + clothingClass;
                if (GetGame().ConfigGetInt(path + " scope") != 2)
                    continue;
                string label;
                GetGame().ConfigGetText(path + " displayName", label);
                string identity = clothingClass + " " + label;
                identity.ToLower();
                if (!identity.Contains("mmg") && !identity.Contains("mighty"))
                    continue;
                if (pass == 0 && !identity.Contains("black"))
                    continue;
                TStringArray slots = new TStringArray();
                GetGame().ConfigGetTextArray(path + " inventorySlot", slots);
                if (slots.Find(slotName) < 0)
                    continue;
                EntityAI clothing = player.GetInventory().CreateAttachmentEx(clothingClass, slotId);
                if (clothing)
                {
                    Print("[MovementLab Gear] " + slotName + "=" + clothingClass);
                    return;
                }
            }
        }
        MovementLabAddItem(player, fallbackClass);
        Print("[MovementLab Gear] No loaded MMG clothing for " + slotName + "; native black fallback.");
    }

    protected void MovementLabEquipTestPlayer(PlayerBase player)
    {
        // SNAFU Weapons is an external Workshop dependency, not redistributed.
        string availableRifle = MovementLabFindSnafuWeapon("rifle");
        if (availableRifle == "")
        {
            Print("[MovementLab SNAFU] Pack absent or no recognized rifle; native fallback only. Send logs for exact class selection.");
            MovementLabEquipNativeFallback(player);
            return;
        }
        MovementLabEquipMMGClothing(player, "Body", "TacticalShirt_Black");
        MovementLabEquipMMGClothing(player, "Legs", "CargoPants_Black");
        MovementLabEquipMMGClothing(player, "Feet", "MilitaryBoots_Black");
        MovementLabEquipMMGClothing(player, "Gloves", "TacticalGloves_Black");
        MovementLabEquipMMGClothing(player, "Headgear", "BallisticHelmet_Black");
        MovementLabEquipMMGClothing(player, "Mask", "BalaclavaMask_Black");
        MovementLabEquipMMGClothing(player, "Vest", "PlateCarrierVest_Black");
        EntityAI snafuPack = player.GetInventory().CreateAttachment("MovementLabTestBackpack");
        if (!snafuPack)
            snafuPack = player.GetInventory().CreateAttachment("AssaultBag_Black");
        if (!snafuPack)
            snafuPack = player;
        // Reserve the two M67s before the gun/magazine loadout fills cargo.
        MovementLabRefillGrenades(player);
        MovementLabAddSnafuWeapon(player, snafuPack, "rifle");
        MovementLabAddSnafuWeapon(player, snafuPack, "sniper");
        MovementLabAddSnafuWeapon(player, snafuPack, "smg");
        MovementLabAddSnafuWeapon(player, snafuPack, "pistol");
        // Extra sniper removed; M24 is the only requested sniper.
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
        MovementLabRefillGrenades(player);
        player.SetAllowDamage(false);
        player.GetStatWater().Set(player.GetStatWater().GetMax());
        player.GetStatEnergy().Set(player.GetStatEnergy().GetMax());
        GetGame().SelectPlayer(null, player);
        MovementLabSpawnRangeFixtures(player);
        m_MovementLabInfectedRange = new MovementLabInfectedRange(player);
    }

    protected void MovementLabRefillGrenades(PlayerBase player)
    {
        if (!player || !player.IsAlive() || GetGame().IsMultiplayer())
            return;
        int now = GetGame().GetTime();
        if (now < m_MovementLabGrenadeNextCheck)
            return;
        m_MovementLabGrenadeNextCheck = now + 250;
        array<EntityAI> items = new array<EntityAI>();
        player.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, items);
        int grenadeCount = 0;
        for (int i = 0; i < items.Count(); i++)
        {
            if (items[i] && items[i].GetType() == "M67Grenade")
                grenadeCount++;
        }
        // The held grenade is included in player inventory traversal. Do not
        // refill merely because it moves from backpack to hands or is unpinned.
        EntityAI backpack = player.FindAttachmentBySlotName("Back");
        while (grenadeCount < 2)
        {
            EntityAI grenade;
            if (backpack)
                grenade = backpack.GetInventory().CreateEntityInCargo("M67Grenade");
            bool inBackpack = grenade != null;
            // A missing/full backpack must not silently disable the supply.
            if (!grenade)
                grenade = player.GetInventory().CreateInInventory("M67Grenade");
            if (!grenade)
            {
                if (!m_MovementLabGrenadeSpaceWarning)
                    Print("[MovementLab Grenades] ERROR: no inventory space for M67; refill will retry.");
                m_MovementLabGrenadeSpaceWarning = true;
                return;
            }
            grenadeCount++;
            m_MovementLabGrenadeSpaceWarning = false;
            Print("[MovementLab Grenades] Created M67; backpack=" + inBackpack + " carried count=" + grenadeCount);
        }
    }

    protected void MovementLabSpawnRangeFixtures(PlayerBase player)
    {
        vector npcPosition = player.GetPosition() + m_MovementLabRangeDirection * 8;
        npcPosition[1] = GetGame().SurfaceY(npcPosition[0], npcPosition[2]) + 0.1;
        m_MovementLabMaleTarget = MovementLabCreateRangeTarget(false, npcPosition, player.GetOrientation());
        vector femalePosition = npcPosition + "3 0 0";
        femalePosition[1] = GetGame().SurfaceY(femalePosition[0], femalePosition[2]) + 0.1;
        m_MovementLabFemaleTarget = MovementLabCreateRangeTarget(true, femalePosition, player.GetOrientation());

        vector carPosition = player.GetPosition() + "6 0 0";
        carPosition[1] = GetGame().SurfaceY(carPosition[0], carPosition[2]) + 0.25;
        CarScript gunter = CarScript.Cast(GetGame().CreateObjectEx("Hatchback_02", carPosition, ECE_PLACE_ON_SURFACE));
        if (gunter)
        {
            gunter.SetOrientation(player.GetOrientation());
            // Native Gunter setup supplies four mounted wheels, doors, hood,
            // trunk, engine essentials, headlights and all operating fluids.
            gunter.OnDebugSpawn();
            EntityAI battery = gunter.FindAttachmentBySlotName("CarBattery");
            if (battery && battery.GetCompEM())
                battery.GetCompEM().SetEnergy(battery.GetCompEM().GetEnergyMax());
            Print("[MovementLab Range Gunter] Equipped and filled car at " + carPosition);
        }
        else
            Print("[MovementLab Range Gunter] ERROR: car could not be created.");
    }

    protected PlayerBase MovementLabCreateRangeTarget(bool female, vector position, vector orientation)
    {
        string survivorClass = "SurvivorM_Denis";
        if (female)
            survivorClass = "SurvivorF_Eva";
        PlayerBase target = PlayerBase.Cast(GetGame().CreatePlayer(null, survivorClass, position, 0, "NONE"));
        if (!target)
        {
            Print("[MovementLab Range NPC] ERROR creating " + survivorClass);
            return null;
        }
        target.MovementLabSetRangeTarget(female);
        target.SetAllowDamage(true);
        target.SetOrientation(orientation);
        if (!female)
            target.MovementLabStartRangePatrol();
        if (female)
        {
            target.GetInventory().CreateAttachment("Hoodie_Red");
            target.GetInventory().CreateAttachment("Jeans_Blue");
            target.GetInventory().CreateAttachment("AthleticShoes_Blue");
        }
        else
        {
            target.GetInventory().CreateAttachment("TacticalShirt_Black");
            target.GetInventory().CreateAttachment("CargoPants_Black");
            target.GetInventory().CreateAttachment("MilitaryBoots_Black");
        }
        target.GetStatWater().Set(target.GetStatWater().GetMax());
        target.GetStatEnergy().Set(target.GetStatEnergy().GetMax());
        Print("[MovementLab Range NPC] Spawned " + survivorClass + " at " + position);
        return target;
    }

    protected void MovementLabUpdateRangeTargets()
    {
        if (m_MovementLabMaleTarget)
        {
            m_MovementLabMaleTarget.MovementLabUpdateRangePatrol();
            m_MovementLabMaleTarget.MovementLabUpdateRangeRagdoll();
        }
        if (m_MovementLabMaleTarget && !m_MovementLabMaleTarget.IsAlive())
        {
            if (m_MovementLabMaleRespawnAt == 0)
            {
                m_MovementLabMaleDeathPosition = m_MovementLabMaleTarget.GetPosition();
                m_MovementLabMaleDeathOrientation = m_MovementLabMaleTarget.GetOrientation();
                m_MovementLabMaleRespawnAt = GetGame().GetTime() + 8000;
                // Male ragdoll remains active until corpse replacement at
                // death + 8 seconds; no earlier ragdoll cutoff.
            }
            else if (GetGame().GetTime() >= m_MovementLabMaleRespawnAt)
            {
                GetGame().ObjectDelete(m_MovementLabMaleTarget);
                m_MovementLabMaleTarget = MovementLabCreateRangeTarget(false, m_MovementLabMaleDeathPosition, m_MovementLabMaleDeathOrientation);
                m_MovementLabMaleRespawnAt = 0;
            }
        }
        if (m_MovementLabFemaleTarget)
        {
            m_MovementLabFemaleTarget.MovementLabUpdateRangeRagdoll();
            m_MovementLabFemaleTarget.MovementLabUpdateRangeRecovery();
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
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        MovementLabUpdateRangeTargets();
        if (m_MovementLabInfectedRange)
            m_MovementLabInfectedRange.Update();
        MovementLabRefillGrenades(player);
        // Fixed ten spare magazines per weapon; no additional AK magazine sampler.
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
                mode = "CTRL WALK / SHIFT JOG / DOUBLE SHIFT SPRINT";
            string message = "[MovementLab Ctrl Modes v10] " + mode + " - Responsive body turning enabled. F7 compares vanilla. Ctrl selects walk1; Shift selects jog2; double Shift selects sprint.";
            player.MessageStatus(message);
            Print(message);
            m_MovementLabAnnounce = false;
        }
    }

    override void OnMouseButtonPress(int button)
    {
        super.OnMouseButtonPress(button);
        if (button == MouseState.RIGHT && !m_MovementLabRightADSDown)
        {
            m_MovementLabRightADSDown = true;
            m_MovementLabRightADSTime = GetGame().GetTime();
            m_MovementLabRightADSEligible = GetGame().GetInput().HasGameFocus() && !GetGame().GetUIManager().GetMenu();
            if (GetGame().GetMission().IsPaused())
                m_MovementLabRightADSEligible = false;
        }
    }

    override void OnMouseButtonRelease(int button)
    {
        super.OnMouseButtonRelease(button);
        if (button == MouseState.RIGHT && m_MovementLabRightADSDown)
        {
            m_MovementLabRightADSDown = false;
            int directADSTapDuration = GetGame().GetTime() - m_MovementLabRightADSTime;
            if (m_MovementLabRightADSEligible && directADSTapDuration >= 0 && directADSTapDuration <= 200)
            {
                PlayerBase directADSPlayer = PlayerBase.Cast(GetGame().GetPlayer());
                if (directADSPlayer)
                    directADSPlayer.MovementLabRightClickADS();
            }
            m_MovementLabRightADSEligible = false;
        }
    }

    override void OnKeyPress(int key)
    {
        super.OnKeyPress(key);
        if (key == KeyCode.KC_F9 && !m_MovementLabViewmodelF9Down)
        {
            m_MovementLabViewmodelF9Down = true;
            MovementLabViewmodelUI.Toggle();
        }
        if (key == KeyCode.KC_F10 && !m_MovementLabViewmodelF10Down)
        {
            m_MovementLabViewmodelF10Down = true;
            MovementLabViewmodelUI.CycleFrame();
        }
        if (key == KeyCode.KC_LMENU && !m_MovementLabAltDown)
        {
            m_MovementLabAltDown = true;
            m_MovementLabAltTime = GetGame().GetTime();
        }
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
        if (key == KeyCode.KC_F9)
            m_MovementLabViewmodelF9Down = false;
        if (key == KeyCode.KC_F10)
            m_MovementLabViewmodelF10Down = false;
        if (key == KeyCode.KC_LMENU && m_MovementLabAltDown)
        {
            m_MovementLabAltDown = false;
            if (GetGame().GetTime() - m_MovementLabAltTime <= 200)
            {
                PlayerBase altPlayer = PlayerBase.Cast(GetGame().GetPlayer());
                if (altPlayer)
                    altPlayer.MovementLabToggleAltADS();
            }
        }
        if (key == KeyCode.KC_F8)
            m_MovementLabAimF8Down = false;
    }

    override void OnMissionFinish()
    {
        if (m_MovementLabInfectedRange)
            m_MovementLabInfectedRange.Shutdown();
        m_MovementLabInfectedRange = null;
        if (m_MovementLabMaleTarget)
            GetGame().ObjectDelete(m_MovementLabMaleTarget);
        if (m_MovementLabFemaleTarget)
            GetGame().ObjectDelete(m_MovementLabFemaleTarget);
        m_MovementLabMaleTarget = null;
        m_MovementLabFemaleTarget = null;
        MovementLabViewmodelUI.Shutdown();
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
