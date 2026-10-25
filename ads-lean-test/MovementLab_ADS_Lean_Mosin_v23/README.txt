Lean range v23 — more upright comfortable walking lean

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Existing full-auto AK74/Mosin range retained.

Standing aimed/leaning movement, both directions: reduce the authored torso sideways bend to40% (about10.4 degrees instead of26 degrees). Apply an inverse rotation pass removing75% of native extra forward pitch during custom lean. The native forward-pitch Collision item is untouched. Neck1 counter-rotation compensates for removed torso roll so the head does not receive an unintended new roll from straightening the body.

Player and NPC use identical corrections. Stationary standing/crouched poses, crouched movement, walking pelvis/legs/foot IK, head-exposure offsets, hands and gun cant remain unchanged in the graph. Actual head/hand positions can move naturally with the straighter parent torso. Weapon-specific grip, sight alignment and native appearance need a visual test.

AK74 full-auto, attachments/unlimited ammo, Mosin backup, NPC patrol, ragdoll and1-second respawn are unchanged from v22. F10 pauses NPC; F8 third-person inspection; F6 head tilt comparison; F7 full lean comparison; F9 measurements. If wrong, send a screenshot and Collect-Logs.cmd ZIP (v23).
