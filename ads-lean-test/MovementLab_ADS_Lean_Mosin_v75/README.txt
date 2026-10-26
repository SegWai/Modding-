MovementLab lean test v75 — v71 raised-camera handoff test

Based directly on v71. Pose graph, smoothing, grip solver and sight/optic camera unchanged.
Raised first-person camera uses position-only wrist binding, keeping native DayZ view rotation and heading. Existing eye-position calculation and interpolation timing retained.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd.
Test: keep the mouse still while facing a landmark. Hold Q, raise/lower, then repeat with E. The view should not turn or roll with the wrist during the raise. Then check looking up/down, support grip, actual ADS and third person.
F7 custom/native comparison. Ctrl+F9 support-hand correction comparison. No batch menu.
Run Collect-Logs.cmd after testing. Local source/package checks only; native compilation and visual behavior require Windows DayZ.
