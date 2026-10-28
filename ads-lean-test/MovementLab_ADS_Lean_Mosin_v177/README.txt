V177: DIAGNOSTIC COUNTER COMPILE FIX

V176 failed World compilation before gameplay: native Enforce rejects ++ on
indexed counter values. The two increments now use temporary scalar variables
and explicit indexed assignment. No arm motion, baseline, graph, controls or
saved settings changed from v176. Native recompile remains to be tested.

V176: WALKING ARM REFERENCE STABILITY TEST

Fixes unnecessary walking-arm reference invalidation: unchanged slider events
and values no longer count as edits; same-side selection is a no-op; side
selection no longer changes weapon geometry revision. Downstream F7 body edits
no longer invalidate the walking F6 arm reference. Initial left-arm capture
waits for the earlier legacy pole calibration, then is cached. Real weapon or
weapon hold edits still invalidate the reference. Saved zero baseline unchanged.

Keep F6 or F7 open with LEFT selected, do not touch sliders, watch for 6 seconds.
If rotation persists, Collect Logs contains a bounded read-only trace of arm
references, fixed correction coefficients and actual bone positions, to separate
native walking/IK motion from recalibration. At most12samples per side, no UI
notifications or continuous file writes. Native walking itself still animates.

The current uploaded pose, stationary preset, graph, native aim/IK configuration,
NPC gait loop, right/left controls and v2 combined save remain unchanged.
Native compilation and resolution of the reported oscillation require testing.

V175: V174 COMPILER FIX

The v174 World module failed at the unqualified Weapon helper calls.
Both conversion helpers now have distinct descriptive names and qualified
calls. No pose math, preset values, zero baseline, graph, controls or save
schema changed. Native recompilation and gameplay still need testing.

V174: UPLOADED WALKING POSE / LEFT ARM ZERO REBASE

Use a fresh extracted folder. The exact uploaded walking settings are retained
as the visible starting pose, including gun, body and the current left arm.

F6 left-arm pitch/yaw/roll now start at ZERO on both lean sides.
F7 left shoulder, upper arm, forearm/elbow and hand XYZ/rotations start at ZERO.
Zero means the uploaded pose, NOT the older unadjusted pose. The baseline is
added internally before the unchanged graph/arm solver. Further slider edits
are offsets from that baseline with the usual +/-90 F6 or +/-45 F7 range.
For example left-lean F6 yaw 0 means the former +57.9000015 degrees. A new
+10 means +67.9000015 internally. This is extra control range, not a guarantee
that extreme new angles will avoid clipping or be physically reachable.

Both sides, all values and the zero baseline save together in
Profiles/LeanMosin/MLWalkingLeanPreset.json (PresetVersion 2).
The baseline is embedded; keep that file whole. Older version-1 absolute
walking saves migrate once against the shipped uploaded arm baseline.
The uploaded original remains archived in the repository as a backup.

Red NPC remains the approved stationary reference. Blue NPC walking-in-place
is edited by F6/F7. Selection holds both on the same side. RMB navigation,
Ctrl+F1 comparison, Ctrl+F8 comparison and X freeze remain unchanged.
Player/stationary approved MLLeanPreset.json is unchanged. These walking edits
still affect only blue. Native compilation/rendering/grip/clipping need testing.
