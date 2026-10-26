LEAN TEST v67 — APPLY AIM AFTER THE CUSTOM POSE
Previous fixes moved individual wrists after the graph had already aimed the
rifle, causing separation and feedback instability. Those fixes remain removed.
v67 neutralizes native vertical aim inside the custom-lean pose branch, builds
the existing level pose, then pitches Spine3 and its descendants together in
the same graph evaluation. Both arms, hands, head and rifle share that motion.
A final no-solve weapon publisher updates attachment after the common rotation.
The lower spine, hips, legs, existing elbow/hold geometry and first-person camera
code are unchanged. Vertical aim can naturally pitch the upper chest; level
poses remain the same. Native non-lean aiming remains available as before.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold level raised aim without lean for 2 seconds (camera reference). Test both
lean sides while looking up/down slowly, then quickly; compare both views.
Check correct up/down direction, grip contact, and extreme-angle clearance.
F7 native/custom, F9 diagnostics, F10 NPC pause. Hold level aim on each lean
side before pitching for a grip-drift baseline. New MLAIM67 logs compare native
aim pitch, actual rifle pitch and weapon-local wrist drift.
Close DayZ, Collect-Logs.cmd.
Offline graph and rigid-transform checks passed. Actual native visual result
is not verified here; Windows DayZ testing is still necessary.
