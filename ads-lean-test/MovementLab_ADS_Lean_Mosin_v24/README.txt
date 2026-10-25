Lean range v24 — marked-side rifle/arm shift

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Existing AK74/Mosin shooting range retained.

Follow the red mark: for a front-facing NPC, picture-left shoulder is his anatomical right. This test uses that direction (positive local right movement/lean) and shifts both shoulder/arm roots8cm toward the marked side while moving in custom aimed lean. It runs BEFORE native weapon IK so the rifle/right hand/supporting left hand are solved together. No separate post-IK rifle teleport. It does not apply while stationary, leaning to the other side or using native comparison. The same graph and F5 scale apply to player and NPC.

F5 toggles this shift ON/OFF during movement, enabled by default. F10 pauses NPC; because the shift is moving-only it fades out when paused, so compare F5 while he is walking. F9 logs rifle position in actor model space and head/joint diagnostics. F6 head tilt comparison; F7 full lean comparison; F8 third-person inspection.

The existing registered TestFloat0..1 controls only the comparison scale. Its ID is validated against all existing bindings before writing. The GCT is unchanged. Upright torso, head/leg corrections, weapon cant, equipment, unlimited ammo, ragdoll and1-second respawn remain.

Native render, shoulder skin/grip quality, sight alignment and the screen-vs-character movement interpretation require a game test. If this applies on the opposite walk direction from what you intended, identify screen-left or anatomical left and send a screenshot with the Collect-Logs.cmd ZIP(v24).
