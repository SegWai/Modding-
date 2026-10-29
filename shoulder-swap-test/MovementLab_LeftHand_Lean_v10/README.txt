FIXED LEFT-HAND TEST V10

Camera stays left, native height/distance; no swap binding.
Left hand uses mirrored trigger grip. Right support wrist now targets the
original support contact transported by the SAME rigid transform as the gun;
finite, cached two-bone solve preserves limb lengths and wrist/finger rotation.
Unreachable targets are logged and keep the mirrored arm (never stretch it).

Stationary upright centred lowered AND raised/ADS stance now mirrors the spine/shoulders
and exchanges left/right leg pose, including foot fore/aft positions. Thus the
right shoulder leads and the opposite foot trails relative to the source pose.
Leaning, moving and crouching retain their previous torso/leg pose; arm roles
remain left trigger/right support. Saved four preset JSON banks unchanged.

Extract fresh; run Launch-Mosin-Lean-Test.cmd without the original lean mod.
This is experimental. Native weapon-helper publishing/rendered grip, firing,
ADS, clothing and stance transitions must be checked in DayZ. Lowered/raised
reference caches are separate; reload/weapon-manager actions disable the layer.
Offline checks
cannot confirm actual contact. Moving lowered/reload actions remain native.
