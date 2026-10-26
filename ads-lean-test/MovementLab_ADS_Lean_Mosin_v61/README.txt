LEAN TEST v61 — v60 COMPILER FIX
v60 could not compile World: nested vector indexing baseRotation[0][column]
was rejected by Enforce. v61 extracts each vector before component indexing.
Camera and animation graph are unchanged from v60. Visual corrections could
not be tested in v60 because startup failed. Native compilation remains pending.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
After startup, raise the gun LEVEL without leaning for 2 seconds. Then test
both lean sides, looking level/up/down, in first and third person.
If startup or the visual test fails, close DayZ and use Collect-Logs.cmd.
F7 comparison, F9 diagnostics, F10 NPC pause. Runtime essentials only.
