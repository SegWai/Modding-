MovementLab lean test v97 — left-moving elbow angles

Replaces the v96 centimetre-offset target with right upper arm about 80 degrees from down (outward flare), left upper arm 45 degrees down below shoulder. On the captured reference this requires moving both hand/weapon targets together about 7.4cm model-left, 9.8cm down and 8.5cm back to keep the left arm reachable. Hand orientations, relative grip, arm lengths and non-arm body bones are preserved.
Based on v95: modifies its existing left-moving arm joint rotations for the new hold, then applies elbow bend-plane alignment after the main grip with same-side hand restoration. V96 branch is not stacked. Right-moving pose and lowering stay exactly v95/v94. First-person, stationary/crouched paths, camera and timing unchanged.
Ctrl+F8 remains shared ON/OFF. ON includes lowered holds/new left elbow pose; OFF returns to v89 baseline. Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd. Test moving left elbows and both grips, then compare right. Collect-Logs.cmd collects diagnostics.
Local geometry/scope/package checks only; actual native angle/placement requires Windows DayZ testing.
