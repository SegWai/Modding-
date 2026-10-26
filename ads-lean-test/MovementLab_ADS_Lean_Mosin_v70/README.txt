LEAN TEST v70 — NATIVE GRIP TIMING REFINEMENT
User confirmed v69 camera tracking fixed and grip slips only while view moves.
v70 retains the entire v69 camera implementation. It selects a native two-hand
weapon IK path during custom lean with both chains continuously active and no
separate IK blend-in/out delay. It runs BEFORE the authored custom pose and
shared yaw/pitch. The existing eased lean gate blends native/custom paths.
Normal non-lean IK remains unchanged. No hand-placement/rotation offsets,
scripted wrist target feedback, target proxies or camera speed edits added.
Authored poses, rifle attachment/roll and approved camera tilt are preserved.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold neutral raised aim level 2 seconds. Hold each lean still about 1 second,
then turn/aim slowly and quickly, both sides. Also check walking lean and ADS.
F7 comparison, F9 diagnostics, F10 NPC pause. Close DayZ, Collect-Logs.cmd.
Grip baselines now wait for the held direction to settle before recording.
Source/graph/PBO checks passed; native grip timing still needs your test.
