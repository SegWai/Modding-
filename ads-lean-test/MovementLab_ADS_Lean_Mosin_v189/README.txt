APPROVED PRESETS COMBINED - V189

All FOUR user-approved JSONs installed exactly as root, bundled fallback and
active profile defaults: MLLeanPreset (standing armed), MLWalkingLeanPreset,
MLCrouchLeanPreset, MLUnarmedLeanPreset. No values rebased or newly mirrored.

Stationary upright normal Q/E lean uses the approved unarmed body pose even
with an object or LOWERED weapon; retains native grip arms as in v187.
Standing raised and upright walking/running keep approved armed banks.
Stationary crouched rifle-raised lean now automatically selects the approved
crouch bank on your character. Separate standing/walking/crouch reference caches;
leaving crouch clears its hold stage. No invented crouch-walking/prone/sprint or
rifle settings forced on pistols. Existing weapon-category safeguards retained.

Original v185 comparison NPC scene, camera, input controls remain. No shoulder
swap experiment. F6/F7 inherited editor context stays unchanged.
Extract FRESH and run Launch-Mosin-Lean-Test.cmd with no other lean mod loaded.
Do not copy old Profiles over these defaults. Original archives preserved.
Offline routing/preset/packaging checks pass; native compile, grip/rendering,
pose matching, transitions and stability are not verified in this workspace.

V189 STARTUP FIX: uploaded v188 native logs show World/Mission compiled, then
held publisher rejected integer 0 for float Weapon Dir LR/UD/Roll fields. These
three expressions now use 0.0. No scripts, poses, JSONs or routing changed.
Native graph reload/gameplay still needs testing; offline checks are not proof.
