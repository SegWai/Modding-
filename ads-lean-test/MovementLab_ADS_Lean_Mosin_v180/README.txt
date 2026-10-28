V180: LEFT WALKING SUPPORT-HAND CONTACT

Your latest uploaded walking preset is included byte-for-byte. This is the
original absolute version1 format: no zero reset or hidden arm baseline.
The v179 minimum-twist shoulder/forearm solver remains intact.

For BLUE NPC LEFT walking lean only, the final native weapon/support-hand solve
now runs even at centred aim, AFTER F6/F7 arm/body edits and late aiming. It
uses the current weapon's native support grip target, so hand contact follows
the weapon in the same graph evaluation, with no scripted chase or smoothing.
No final right/trigger-arm solve is newly enabled. Gun position/muzzle controls,
right arm, all user values, red stationary reference and player conditions stay
unchanged. RIGHT walking lean keeps the previous centred behavior.

The native contact solver may adjust left elbow bend, forearm or wrist orientation
to reach the fore-end. Your editor values are retained, but their exact visual
result cannot override physical contact in this test. It is not a frozen arm;
shoulder and elbow can move naturally while the hand targets the rifle.

F6/F7 edits still target blue only. Save All preserves both sides together in
Profiles/LeanMosin/MLWalkingLeanPreset.json. Native compilation, correct palm
contact, stride stability, elbow shape and actual mesh behavior need testing.

Test LEFT held for several strides from the side and front. If elbow shape shifts
too far from your recording, video plus the newly saved JSON will show what needs
adjustment. No new toggle/control, graph source, node or duplicate-base blend.
