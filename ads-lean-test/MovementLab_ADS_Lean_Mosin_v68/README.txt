LEAN TEST v68 — COUPLE BOTH AIM AXES / USE NATIVE POSE CAMERA
v67 moved pitch after the custom pose but left yaw before it. v68 moves both
axes after pose authoring, shared by arms/head/rifle, using the current graph
AimY/AimIKX. The final publisher does no independent aim or hand solve.
Raised first-person camera now reads the native animation-pose camera matrix,
not the world item transform, while retaining the same neutral-relative framing
and tilt rule. Native ADS/optics code and authored level pose geometry unchanged.
No wrist controllers, procedural feedback or target proxies are used.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold neutral raised level aim for 2 seconds. Test both lean sides, up/down AND
left/right view changes, slowly then quickly, in both views. Hold each side
briefly before moving the view. F7 comparison, F9 diagnostics, F10 NPC pause.
Close DayZ and Collect-Logs.cmd. MLAIM68 now separates hand-to-hand skeleton
drift from weapon attachment/world-item timing. Local transform/source checks
passed; native frame timing/attachment behaviour still needs your DayZ test.
