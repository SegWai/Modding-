LEAN TEST v66 — HAND RECOVERY
v65 made the hand disappear. This recovery removes the failed target proxy and
ALL experimental grip corrections introduced in v58-v65. It restores the entire
v57 arm/pose graph (including the earlier walking and standing pose work).
The first-person camera/tilt code approved during v64 is retained unchanged.
Lean/raise smoothing, standing head travel targets and NPC test remain.
This is a rollback of the broken hand correction, NOT a verified fix for the
original up/down grip separation. That issue remains unresolved.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Raise the gun level without leaning for 2 seconds, then test both lean sides.
The original hands should be visible again without experimental target motion.
If still missing, close DayZ and send Collect-Logs.cmd output plus a short clip.
F7 comparison, F9 diagnostics, F10 NPC pause. Runtime essentials only.
Local checks confirm original graph restored and approved camera unchanged;
Windows DayZ playback has not been run here.
