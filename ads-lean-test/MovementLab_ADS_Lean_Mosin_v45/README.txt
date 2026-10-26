STANDING RIGHT-LEAN POSE TEST v45
This version applies the approved right-lean Blender pose while STANDING STILL
with the weapon raised/aiming and leaning to the CHARACTER'S OWN RIGHT.
It uses the measured v44 standing reference 82178_false and approved v43
right-lean capture 67091_true, with a shared player/NPC graph correction.
Walking, crouching, left lean and native comparison keep their prior steady poses.
First-person raised custom animation remains enabled; existing smoothing retained.

1. Extract to a NEW folder under F:\DayZProjects and launch
   Launch-Mosin-Lean-Test.cmd directly. No batch toggle/menu.
2. Stand still, raise/aim the AK74 and hold E (character right, default controls).
3. Compare the body, arms, head and feet with the approved right-lean Blender pose.
4. Check walking, crouching and Q (left) still behave as before.
F7 compares custom/native. F9 logs the pose and automatically captures the
standing right pose after 0.5 seconds held still. Close DayZ and run
Collect-Logs.cmd if the pose differs or a native graph error appears.
NPC receives the same correction when stationary in the same right-lean state;
its moving patrol remains unchanged. Equipment, ammo and respawn unchanged.

The pose correction runs after hand/foot IK. A final attachment-only pass
publishes the moved right-hand weapon dummy without solving the arms again.
Measured neutral-forward reference reconstructs target to floating-point accuracy;
this is NOT native DayZ playback validation. Idle sway, other aim directions,
other weapon grip offsets and native attachment publication need in-game checking.
The original local facial expression is preserved under the repositioned head.
