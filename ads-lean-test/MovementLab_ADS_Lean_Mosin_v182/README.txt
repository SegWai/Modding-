V182: NATIVE VS CUSTOM CROUCH + LIVE F6/F7 EDITING

Both NPCs are crouched with weapons RAISED, not ADS, 0.5m apart.
RED: default/native lean path, locked read-only, never takes crouch editor data.
BLUE: your custom lean plus F6 weapon/arms/head and F7 body offsets.
Both continue LEFT/CENTRE/RIGHT/CENTRE, one-second targets. Open F6 or F7 and
choose LEFT/RIGHT: both hold that side for comparison; only BLUE gets edits.
Closing the panel resumes the shared automatic cycle. RMB navigation retained.

F6: XYZ weapon position in cm, pitch/yaw/roll, muzzle, arms/elbow direction, head.
F7: 24 body parts, XYZ position and rotation. These panels now edit CUSTOM CROUCH
ONLY, not walking/standing/global player settings. Each side independent.
Initial crouch offsets are zero relative to the existing custom crouch, with
no change to the approved standing or walking JSON or parameter interpretation.
The weapon solver samples the unedited actual crouched arm geometry once per
side, never a hardcoded standing reference. New effects stay off briefly while
sampling; F7 stays off until arm reference settles, avoiding sample feedback.
Weapon targets outside reach retain last valid hold and block saving.

Save All stores BOTH sides, weapon/arms/head/body together in
Profiles/LeanMosin/MLCrouchLeanPreset.json with .bak. Send that file after tuning.
MLLeanPreset.json and MLWalkingLeanPreset.json are preserved exactly, and their
shared player/NPC standing/walking behavior remains as in181. Red is forced onto
the native comparator branch even if CtrlF1 is used. The comparison runs within
the modded workspace, not a separate clean game process. Its custom gate and
smoothing are disabled; NPC raised pose still uses visual demo state forcing.

Crouch F6/F7 edits affect only blue. Direct F7 limb edits can alter reach/grip;
F6 elbow controls guide bend direction, with flexion following shoulder/hand
distance. Native compilation, all sliders, current crouch references, contact,
mesh behavior and actual default/custom comparison still need native testing.
Use a fresh extracted folder; older profile saves override bundled files.
