V183 - STANDING UNARMED COMPARISON

RED: default DayZ standing lean, empty hands, weapon/aim state off, read-only.
BLUE: your approved standing aiming BODY posture, with native lowered unarmed
arms instead of rifle shoulders/arms. No gun is spawned on either NPC.
Same Denis character, clothing sizes, native scale and 0.5m centre spacing.
Natural pose height is retained; no scale or extra height offset is applied.
LEFT / CENTRE / RIGHT / CENTRE: one-second targets, native-speed interpolation.

F6: left/right upper-arm and head rotations. Opens directly on Arms/Head.
The weapon tab is hidden because there is no weapon/muzzle to edit.
F7: all 24 body parts, XYZ and rotation, including forearm/elbow/hand/feet.
Opening a panel holds BOTH NPCs on the selected side; only BLUE is edited.
RMB navigation while the panel remains open is retained.
Save All in either panel writes both sides/all fields to
Profiles/LeanMosin/MLUnarmedLeanPreset.json. Use this NEW save for this experiment.
It does not overwrite your standing-aim, walking-aim or crouch presets.

Your supplied MLCrouchLeanPreset.json is the new approved crouch base, copied
EXACTLY to root, active profile and bundled default, and archived in GitHub.
Approved standing and walking files are also preserved byte-for-byte.
Player weapons and ordinary character aiming/lean behavior are unchanged.

BLUE samples its native unarmed skeleton once per side, with all new outputs
zero, then applies cached body-only corrections. Let both sides cycle once.
There is NO temporary gun, raised-arm phase, weapon IK or per-frame recapture.
The target body frames derive from existing captured/approved standing pose
heritage plus its current saved body/head edits. Arm/shoulder edits are excluded
so the unarmed arms can hang naturally. F6 now rotates upper arms directly;
F7 forearms/hands let you bend the elbows without fixed-wrist rifle constraints.

Offline graph/math/archive/PBO checks do not replace a native DayZ test.
Windows compilation, exact rendered posture, clothing and FPS are NOT RUN here.
Fresh extraction avoids an old active profile overriding the included defaults.
