Lean range v35 — correct final gun aiming direction

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects.

V34 final grip solver published the weapon orientation with its aim stage disabled; your screenshot shows the barrel pointing upward. V35 enables final aiming with the same boolean reference-hold gate as both hand chains, using the original NormalWeaponIK horizontal/vertical aim expressions and signed weapon-cant target. The final pass solves aim and hand grips together before publishing the weapon attachment.

Existing arm-pose rotation values, body/head/leg/gait nodes, equipment, ammo, ragdoll and respawn are unchanged. Same graph for player and NPC. The final native solver can adjust hand/weapon placement to achieve its targets; exact visible hold and gun direction must be checked in-game.

Starts enabled. F5 reference hold comparison; F6 head comparison; F7 native/custom; F8 inspection; F9 diagnostics; F10 pause. Collect-Logs.cmd creates the v35 log ZIP if needed.

Included authoring PNGs remain v32 previews and do not demonstrate the native final solver outcome.
