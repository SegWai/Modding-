LEAN TEST v65 — SAME-FRAME SUPPORT GRIP TARGET
The supplied v64 video shows separation; logged target gap reached 21cm.
v65 removes all per-frame positional/rotational feedback. Calibration records
one fixed support-wrist transform relative to the rifle-holding right wrist.
The graph constructs that target from the CURRENT primary wrist, captures it,
restores the primary wrist exactly, then solves the left arm in that same pose.
No growing correction offsets, frame-delayed weapon target or correction filter.
The approved first-person rifle-tilt/camera code is unchanged from v64. No gun
or trigger-hand pose settings changed; the temporary target proxy is restored
before output. Native support solve is shared by player and NPC.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Raise the gun LEVEL without moving/leaning for 2 seconds to record its grip.
Then test LEFT/RIGHT looking level/up/down, slowly then quickly; both views.
F7 comparison, F9 diagnostics, F10 NPC pause. Close DayZ, Collect-Logs.cmd.
New logs show fixed_primary_local_grip (must stay constant for that weapon) and
actual target gap. Local transform/inverse tests passed; the native cross-hand target
capture/solve still needs Windows DayZ validation. Runtime essentials only.
