# v104 failed crawling trace and v105 correction

The user's v104 upload contains11 deaths:8 activated ragdolls and3 pose-readiness timeouts. Two timeouts are confirmed crawling cases. Both occur after about2s with repeatable head/pelvis positions near0.5907/0.5371 model units. The user reports freezing, a standing/default death transition and no visible crawler ragdoll. One other timeout is an upright raised-arm case, so the arm approximation is also still inadequate.

The freeze/fallback mechanism is established by source and logs: v104 freezes the original, waits for initialization, then Stop restores the original simulation when the height gate times out. That allows the native death animation to resume. The earlier interpretation that0.54m pelvis height must be an unfinished transition was not justified. Model-space height is not terrain clearance; the consistent head-forward torso layout is compatible with native prone pose plus animation/root offsets.

v105 removes those hard height cutoffs. A crawling replacement must report native prone stance, have initialized transforms, show a mostly horizontal head-to-pelvis torso direction, and remain stable for100ms. Model-space transforms are bounded for invalid values but not interpreted as distance from the ground. The existing2s deadline, visibility guards and failure cleanup remain.

Before source death handling, v105 also captures a valid pelvis world position. At activation, the native replacement's pelvis model offset is transformed into world coordinates and subtracted from that source anchor to choose the replacement root position. This aligns pelvis centers before physics; it does not set positions continuously after ragdoll starts. It is not full-bone pose cloning and native controller/physics interpretation of the adjusted root remains a visual check.

The actual adapted helper/sample/capture methods pass existing momentum/rollback tests plus acceptance of head0.59113/pelvis0.53707 with native prone/horizontal torso, rejection of a vertical torso, and world-pelvis alignment within0.0001 in the mathematical mock. SDK source confirms the native stance accessor and model-to-world API. These do not verify native rendering/physics. PBO/source/checksum and ZIP integrity are checked at packaging.

Running arms and arbitrary attack/idle pose continuity remain unresolved. v105 retains approximate native Human pose preparation; exact-frame pose transfer is not implemented. The separate captured-pose converter/graph-fragment groundwork is offline only and not loaded by v105. No further arm retest is requested for this build.

Extract MovementLab_Corpse_Momentum_v105.zip into a fresh folder, launch, kill a fully crawling infected and check for ground-level ragdoll instead of freeze/standing/default fall. Close DayZ and run Collect-Logs.cmd for MovementLab-Corpse-v105-Logs.zip. Native compilation, prone readiness and pelvis placement still require the local run.
