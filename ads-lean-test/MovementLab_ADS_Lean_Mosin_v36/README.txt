Lean range v36 —95% standing-height walking lean target

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Stand neutral briefly at launch so your height reference can be captured. NPC captures the same reference before patrol.

Uses each actor's neutral standing Head-bone height as a practical height proxy and targets95% of it while fully leaning, standing and walking/jogging in ADS. A smoothed pelvis-height correction runs BEFORE the existing native walking foot IK, allowing the native leg solver to straighten knees while preserving its gait/foot targets. Works identically for player/NPC and both lean directions. No mesh scaling or actor teleporting.

Weapon-hold/grip/aim/cant node settings are byte-identical to v35. Range loadout/ammo/ragdoll/respawn remain. Crouched legs and stationary planted stance unchanged. Correction fades when no longer in aimed leaning locomotion.

95% is a target for calibrated head-bone height, not a verified full-mesh crown height or every instantaneous step. Smoothing preserves gait bob; leg reach and safety limits can prevent exact target attainment. Native knee/foot contact and gun alignment still require an in-game check.

F9/status logs report standing_head_y, current_head_y, height_lift_m, height_bound and observed_head_height_ratio. F5 reference gun-hold comparison; F6 head comparison; F7 native/custom; F8 inspection; F10 pause. Collect-Logs.cmd makes the v36 log ZIP. Included PNGs are previous v32 arm-authoring previews, not previews of the new runtime leg/height controller.
