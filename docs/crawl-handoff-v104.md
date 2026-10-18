# v103 crawling trace and v104 correction

The second v103 log upload contains a newer session with14 deaths, including one confirmed crawler. On that crawling death, detection was true and the replacement activated/revealed ragdoll. There was no pose timeout. Activation head height was0.591130 and pelvis height0.537070 model units. The user observed a momentary standing body followed by a ground-level normal-looking death without visible ragdoll. The ragdoll flag therefore did not establish a successful visible handoff.

v103's head<0.8/pelvis<0.65 check admitted this intermediate-height pose. It did not require native prone stance or settling. In addition, the original infected remained animated during replacement warmup, while the replacement's hidden state was only set once and could be affected by native creation/death updates. The logs do not identify which actor produced the standing flash; both paths are guarded in v104.

## Change

- After confirmed native death, the tracked original's simulation is frozen until the replacement takes over. Failure/cleanup restores it through the existing rollback path; no unmanaged corpse is left frozen after a failed creation.
- The dedicated replacement starts unpublished/hidden in its script constructor. Its visibility state is reasserted in POSTFRAME until deliberate reveal. The helper uses that per-instance visibility state rather than hiding once during creation.
- Crawlers require native prone stance, head height0.02..0.5, pelvis height0.02..0.35 and a low-pose hold of100ms. The pose may move no more than0.025 model units from its settling anchor; otherwise the hold restarts. This rejects the actual logged intermediate pose. The warmup budget for crawlers increases to2s; the five-second confirmed-death respawn deadline remains unchanged.

The native thresholds and timing still require local testing; they are not derived from a proven full prone clip. If they reject a legitimate prone pose, the test logs should guide adjustment. A stance-readiness condition does not provide exact infected-frame matching.

## Scope and verification

The confirmed momentum path remains. v104 is a focused crawl-transition/visibility change, not the requested full animation-frame pose transfer. Standing/attack/arm poses still use v103's approximate native seeding. Full captured-pose conversion groundwork is documented separately and is not installed in this game package.

Actual adapted helper/capture/sample methods pass C++ logic checks, including rejection of head0.59/pelvis0.537, waiting for the low-pose hold, restoring an already-frozen original when creation fails, and prior momentum/rollback cases. Native prone stance is mocked in those checks; actual stance-transition and POSTFRAME visibility behavior remain an in-game test. The packager validates PBO source/prefix/offsets/hash and ZIP integrity. No native Enforce compilation or visible result is claimed in the cloud.

Extract MovementLab_Corpse_Momentum_v104.zip into a fresh folder, launch, cause a broken-leg crawl and kill the fully crawling infected. Check for an upright flash and whether the low body actually falls under physics. Close DayZ, run Collect-Logs.cmd and send MovementLab-Corpse-v104-Logs.zip with the visible outcome.
