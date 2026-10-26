MovementLab lean test v93 — existing v39 arm-rotation comparison

Starts from stable v89. Re-solves the captured v39 arm rotations for 12cm total hand lowering versus the original 5cm: an additional 7cm. Changes the existing 18 shoulder/elbow/wrist rotation nodes before native final grip, not a new late translation layer. Captured-reference geometry preserves bone lengths, hand orientations and non-arm bones. Native displacement may differ and is the purpose of this test.
Scope: own-RIGHT moving raised lean, shared third-person player/NPC; left, stationary and first-person paths unchanged. V89 original late 20cm configuration remains untouched for a clean comparison; v90/v91/v92 changes are absent.
IN-GAME Ctrl+F8 toggles new arm rotations ON/OFF, default ON. OFF selects exact original v89 arm rotation values. An unavailable-control message means the test cannot run; collect logs. Do not change F5/Ctrl+F9 during this test.
Watch NPC while it moves to its OWN right; compare Ctrl+F8 ON/OFF across several passes. Record video and run Collect-Logs.cmd. New [MLDROP93] samples log stable right-moving wrist/elbow positions relative to chest/shoulder, mode and bound control. Keep the NPC moving; pausing removes the scoped movement correction.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd. No batch menus.
Native compilation, visual result and final-solver retention are unverified here. Local capture solve, control/scope and package checks only.
