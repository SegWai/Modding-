FRAME 15 STANDING LEFT-LEAN REFERENCE v47
Target confirmed: frame 15 of Captured_Left_Lean_Walk_20261026_061044.blend.
The complete 114-bone target and weapon transform are preserved in
Frame15-Standing-Left-Target.json. This is the character's OWN LEFT.
The v46 body graph/right-standing pose and first-person camera code are retained.
This package COLLECTS THE MISSING BASELINE; it does not apply frame15 yet.

1. Extract into a NEW folder and launch Launch-Mosin-Lean-Test.cmd.
2. On YOUR character, stand still, raise/aim the gun and hold Q (default LEFT).
3. Wait for "Left standing reference captured" (automatic; no key/menu needed).
4. Close DayZ, run Collect-Logs.cmd and send the ZIP.
Only a full custom left lean, erect stance, raised gun and no movement can trigger
this reference. It waits 0.5 seconds for stability and records all 114 bones.
The earlier measured standing reference was RIGHT lean; reusing or mirroring it
would guess the native arm/weapon/foot IK and would not be an exact left transfer.
Walking, crouching, approved right lean and camera behavior are unchanged.
F9 rearms the standing-left collector and optionally records another walking clip.
Existing Blender importer/helper remains available for the walking recording.
Native Windows compilation and reference capture require running DayZ.
