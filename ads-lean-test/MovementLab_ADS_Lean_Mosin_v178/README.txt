V178: FINAL WALKING SUPPORT-GRIP SOLVE

V177 trace confirmed one cached reference and constant correction coefficients
while the left elbow moved vertically by about25cm through the walking cycle.
The final weapon IK support chain was disabled at centred aim, leaving earlier
fixed arm edits on a changing walking base with no final hand-contact solve.

Only the BLUE walking preview now enables final native left/support-arm IK at
centred aim too, after all F6/F7 body and arm edits. Native trigger/right arm
solve remains unchanged: it is NOT newly enabled at centred aim. The weapon
position/angles and saved zero baseline are unchanged. Elbow placement can
adapt to maintain hand contact and may differ from the unsupported saved pose.
This is a native grip solve, not a frozen upper-body animation or a baked pose.
The native arm solve may override independent support-arm/elbow edits; exact
editor influence and visual stability require an in-game test.

Red NPC and player use the same old conditions; no new graph node, source,
control variable, per-frame positional feedback or separate pose was added.
The log-proven editor OnHide null-mission access during shutdown is guarded in
both F6/F7 menus. All actual walking pose settings and version2 save retained.

Test blue on held LEFT for6seconds, then RIGHT. F6/F7 support-arm adjustments
may be constrained by final native grip. If it still swings or the elbow loses
needed adjustment, video plus logs will guide the next change. Native compilation
and visual grip/rotation resolution are NOT yet confirmed.
