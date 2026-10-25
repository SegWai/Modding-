Lean range v29 —15cm right-chest hold during anatomical-left movement

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Range loadout/ammo/respawn/ragdoll retained.

Direction is now the CHARACTER'S OWN LEFT, not screen-left: while walking left, aiming and leaning, shift his solved arm/weapon hold15cm toward his own RIGHT, opposite his travel. The old35cm positive-lean pre-IK shoulder correction is removed.

Implementation: NormalWeaponIK first solves aiming and both grips. A final Model+X translation moves RightArm and LeftArm subtrees together by0.15m, then the existing head passes run. No weapon IK runs afterward. The custom outputweaponoffsettobuffer=true option is removed, restoring the original uploaded native configuration default for attachment output rather than publishing an earlier weapon matrix. Native attachment/grip/camera behaviour still requires in-game validation.

Player and NPC share the correction. All other torso/head/leg/gait nodes and gun rotation/cant expressions are unchanged. No correction while stationary, leaning right, neutral or native comparison.

Offset starts enabled. F5 compares the final15cm hold ON/OFF. Let him complete one full left/right pass, toggle F5, then wait another pass. Automatic chest/weapon/optional hand measurements are retained. F6 head comparison; F7 native/custom; F8 inspection; F9 manual measurements; F10 pause (moving-only shift fades).

If incorrect, close DayZ and run Collect-Logs.cmd. The local tests cannot establish native placement or shooting alignment.
