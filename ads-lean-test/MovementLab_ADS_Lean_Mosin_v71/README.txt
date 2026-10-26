LEAN TEST v71 — SUPPORT CONTACT AFTER AUTHORED ARM OFFSETS
Keeps the fixed camera byte-for-byte apart from version log labels. v70 native
pre-pose grip timing remains. v71 adds a native support-hand contact solve AFTER
the authored arm offsets and BEFORE the shared aim rotation. Primary/trigger-hand
chain is disabled there; no item-offset buffer is published by the added solve.
No scripted wrist controllers, feedback or target proxies are used.
The native solver determines the support grip from the weapon IK profile.
Its effect on the rendered weapon/hand is NOT native-verified here.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold level raised neutral aim for 2 seconds. Test both lean sides, turning slowly
and quickly. Hold each side still about 1 second before moving for diagnostics.
CTRL+F9 toggles ONLY the added post-pose support solver (ON by default).
OFF restores the v70 pose path; camera remains fixed in either mode. Compare the
same lean and movements in ON/OFF. F9 alone measures distances; F7 native/custom;
F10 NPC pause. Close DayZ and Collect-Logs.cmd after the comparison.
No batch menus. Runtime essentials only. Local source/graph checks passed;
Windows DayZ validation of this support-only native solve remains necessary.
