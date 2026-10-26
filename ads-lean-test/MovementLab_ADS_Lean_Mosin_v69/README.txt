LEAN TEST v69 — CAMERA / ARM RENDER SYNCHRONIZATION
Keeps the v68 shared yaw/pitch graph and native pose-camera framing.
The corrected raised view is now expressed relative to RightHand (bone mode3)
rather than an unbound model-space snapshot. The engine samples the interpolated
rifle-holding wrist for camera and rendered arms together. The model-space
camera position/orientation is algebraically unchanged at the current pose.
FOV, native ADS/optic camera code, native firing/input and authored gun pose
settings remain. Custom first-person rifle tilt alignment is retained.

Lean-distance trim and neutral-head calibration now only adjust while looking
within 5 degrees of forward/level. During off-centre look at full standing lean,
the last trim is HELD; it no longer chases a rotating head or fades away.
Distance measurement notices are also restricted to forward/level aim.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold neutral raised level aim 2 seconds, then lean and move the view slowly and
quickly. Compare camera/rifle/arm tracking in both directions; check ADS and
free-look too. Hold forward level Q/E briefly for the reach notices.
F7 comparison, F9 diagnostics, F10 NPC pause. Close DayZ, Collect-Logs.cmd.
MLCAM69 should report bone_mode=3 parent_bone=RightHand during custom raised
lean. reach_held_for_look reports trim hold. Graph/PBO matches v68 exactly;
offline conversion/hold tests passed. Native renderer timing needs your test.
