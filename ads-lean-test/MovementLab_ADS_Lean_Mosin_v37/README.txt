Lean range v37 — directional right elbow

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Stand neutral briefly for the unchanged height calibration.

While walking and aiming/leaning to his OWN RIGHT, tuck his right elbow closer to the torso. While moving to his OWN LEFT, move that elbow slightly outward. Same shared graph for player/NPC. These are character directions, not screen directions.

Implementation captures the right-hand grip AFTER the working final native weapon aim/grip solver, applies a small directional upper-arm bend seed (18 degrees native ModelZ rightward travel, -10 degrees leftward travel), then uses the existing native right-arm IK2 chain to restore the captured hand target. No later weapon aim stage re-centres the rifle. Final elbow angle depends on IK and is not the seed angle. The new branch is gated to standing custom aimed-lean movement and F5 reference hold; optimized away when inactive.

Gun/aim/grip node parameters, left arm, torso/head/leg/gait nodes,95% height controller, range equipment/ammo/ragdoll/respawn remain unchanged. No new controls or script APIs.

Starts enabled. F5 compares reference hold including new elbow branch; F6 head comparison; F7 native/custom; F8 inspection; F9 diagnostics; F10 pause. Native elbow/palm contact and unchanged gun direction require an in-game check. Collect-Logs.cmd creates the v37 ZIP. Included PNGs remain old v32 authoring previews, not native elbow/height previews.
