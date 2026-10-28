V186 - YOUR CHARACTER, ALL FOUR APPROVED LEAN BANKS, NO NPCs

No NPCs are created. The same native AK74/SKS/Glock/backpack loadout remains.
Your own native Q/E, stance, movement and raised/ADS state choose the pose:
- Raised standing: approved MLLeanPreset.json.
- Raised upright walking/running: approved MLWalkingLeanPreset.json.
- Raised stationary crouch with shouldered firearm: approved MLCrouchLeanPreset.json.
- Standing idle, empty hands, fists lowered: approved MLUnarmedLeanPreset.json
  (latest14495byte upload, SHA d47025fd4275847815d0fda2d34b629d057608355e7fb5d47e79f4b71d859a27).
Each of the four files is copied EXACTLY into root, active profile and bundle.
No new mirroring, rebasing, pose edits or separate first-person pose is added.
Other contexts keep existing stance/weapon-appropriate handling: this does not
invent a crouch-walking, prone, sprinting or pistol-specific rifle-arm preset.

For first-use unarmed LEFT, stand centred empty-handed for at least half a second,
then hold left/right lean briefly. Neutral/side snapshots are captured once;
newer edits do not trigger feedback sampling. Native raising, lowering, shooting,
weapon switching and ADS remain under player control. No forced demo clock,
Lean/Raised/ADS writes or movement overrides are applied to the player.
Crouch arm/weapon reference also settles on each full stationary lean once.
Standing/walking/crouch have separate cached arm reference banks.

Third-person weapon-RAISED camera keeps the SAME distance rule (minimum4m).
The old inspection lowering is replaced with a pivot15cm above native while
raised:50cm higher than185 standing,25cm higher than185 crouched.
Lowered camera, first-person and ADS/optic cameras are unchanged.

F6/F7 remain the UNARMED bank editors, now affecting your eligible unarmed pose.
They do not automatically hold/drive Q/E on the player. RMB navigation retained.
Save All writes MLUnarmedLeanPreset.json; other approved banks stay separate.
Use a fresh extraction so stale active profile saves cannot mask approved files.

Offline bank/transition/cache/camera/API/PBO tests passed; native Windows DayZ
compilation, actual pose matching, aiming/grip, FPS and crash stability NOT RUN.
