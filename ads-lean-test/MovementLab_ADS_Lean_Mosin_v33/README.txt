Lean range v33 — final native hand grips

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects.

Your screenshots show the support hand below the actual fore-end after the arm correction. V33 retains all v32 hold/body/leg/head rotation values and adds a final native hand-chain solve AFTER the21 arm/shoulder/wrist correction nodes. It uses the equipped weapon's RightHandOrigin/RightHand_Dummy and LeftHandIKTarget grip configuration. Aim weight is0 and extra WeaponRoll is empty, avoiding another aim/cant correction. Hand-chain weights use the same left-moving custom aimed-lean gate/F5 setting.

The final solver explicitly enables outputweaponoffsettobuffer=true to publish the weapon offset after the pose/grip solve. Earlier README claims that the original uploaded NormalWeaponIK omitted this flag were incorrect: original locomotion.agf line3891 enables it.

Same graph for player and NPC. Offset starts enabled. F5 toggles reference hold; F6 head comparison; F7 native/custom; F8 inspection; F9 diagnostics; F10 pause. Range equipment/ammo/ragdoll/respawn remain.

Native grip contact, final gun placement and camera alignment need an in-game test. No guessed5cm hand offset is applied. Collect-Logs.cmd makes the v33 ZIP.

Included authoring PNGs are unchanged v32 pose previews; they do not display or validate the new native grip solver.
