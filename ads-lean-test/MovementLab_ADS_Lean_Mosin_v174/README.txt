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
