MovementLab lean test v90 — 5cm arms-only lower hold

Returns to the v39 goal of lowering both hand hold targets 5cm while keeping shoulder roots and other body parts fixed. Uses same-side native hand target capture and arm-chain IK to adapt joint bending to the current pose, instead of reusing v39 angles blindly on a different pose. Both hands keep their captured target orientations; rifle attachment is republished after solving.
V88/v89 late whole-arm root translations and 20cm drop are absent. New lowering applies to shared third-person raised player/NPC poses. First-person crouch-style lean from v87, head/torso/legs, camera and timing are unchanged.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Check the hold near the right shoulder, elbow bending, both hand grips and aiming up/down in third person/NPC. Collect-Logs.cmd collects diagnostics.
Local source/target/math checks only. Native IK target capture, shoulder alignment and visual playback need Windows DayZ testing. V87 remains the unlowered rollback.
