Lean range v28 — dedicated weapon-offset control

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Existing range/equipment/ammo/ragdoll/respawn retained.

V27 logs no longer show the graph expression compilation errors, but the visible offset still did not work. V28 replaces native TestFloat with a dedicated MLADSLeanWeaponShift control that defaults to1 (enabled) in the animation graph itself. F5 sets this shared control to0/1 for player and NPC. All pose amounts, including35cm moving anatomical-right shoulder offset, torso/head/leg motion, gait and gun roll, are unchanged. Native IK preserving the offset remains unverified.

The automatic observer no longer requires both hand bones: missing optional hand bones are recorded by their negative indices instead of suppressing all weapon/chest measurements. It uses the SDK attachment-bone names RightHand_Dummy/LeftHand_Dummy.

Leave offset ON for one full left/right pass, press F5 once, and wait another full pass. Close DayZ and run Collect-Logs.cmd; send the v28 ZIP. No manual F9 timing needed. F10 pause removes moving-only offset. F6 head comparison; F7 native/custom; F8 third-person inspection; F9 manual diagnostics.

This is a repair test. Local checks do not establish native appearance or compilation.
