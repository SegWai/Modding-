LEAN TEST v64 — REMOVE SPINNING WRIST / CAMERA FILTER MISMATCH
v63 logs confirm large recursive grip offsets (up to 50cm). v64 removes the
scripted wrist-rotation feedback: all three procedural rotation inputs are zero.
Only support-hand position is corrected, bounded to 12cm, and reset outside lean.
The native arm solver retains the evaluated wrist/finger orientation.
Raised camera position now follows the current rifle pose directly, just like
its orientation, instead of using an independent .12s position filter.
The approved first-person rifle tilt alignment, third-person gun settings and
existing smooth lean/raise controls remain. No graph or pose geometry edits.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold the gun LEVEL without leaning/moving for 2 seconds. Then lean both ways and
look up/down slowly, then faster. Check wrist stability, hand contact and camera
tracking. Compare third person too. F7 comparison, F9 diagnostics, F10 NPC pause.
Close DayZ, Collect-Logs.cmd if needed. Logs report actual hand-target errors.
Offline math/source/PBO checks passed; native visual result needs your test.
