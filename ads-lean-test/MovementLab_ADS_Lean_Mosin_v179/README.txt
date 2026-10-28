V179: LEFT UPPER-ARM TWIST TEST — BASED ON V173

This version follows the requested rollback: ORIGINAL ABSOLUTE sliders,
NO zero reset, NO v174+ baseline schema, NO v178 final support-IK override.
Your uploaded original MLWalkingLeanPreset.json is included unchanged.

The old built-in left elbow correction and F6 left elbow correction swiveled
the whole arm around shoulder-to-wrist. A large correction could twist the
upper arm/sleeve while the inverse wrist rotation hid that twist at the hand.
For BLUE walking NPC only, those two corrections now use the shortest shoulder
swing plus a separate forearm bend. Wrist location, desired elbow location and
palm orientation are preserved in the reference math; axial upper-arm rotation
is avoided. Left-arm treatment applies on either lean side. Red/player use the
old solver and their saved settings. No new position offsets or body pose.

F6 still controls bend DIRECTION, not an independent flexion angle: fixed arm
lengths and shoulder/hand distance determine how much the elbow can bend.
A nearly straight arm needs a closer hand/weapon or appropriate shoulder position
to gain more bend; forcing rotations cannot change bone lengths safely.
F7 is direct bone editing, so extreme values can still distort the sleeve.

F6/F7 blue preview editing, both-side selection, walking in place, native gait,
CtrlF1/CtrlF8/X and the original saves remain as in173. Exact visible cloth,
gait grip, pole direction and F6/F7 behavior need native testing. This does not
claim the previous walking hand oscillation is proven fixed or freeze the gait.
