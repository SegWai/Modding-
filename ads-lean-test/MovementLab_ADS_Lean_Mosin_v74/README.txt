MovementLab lean test v74 — v71 camera-direction correction

Based directly on v71. Keeps v71 poses, smoothing and grip solver.
Raised first-person camera now keeps native DayZ look direction instead of inheriting rifle pose rotation during a lean. Existing eye positioning and wrist synchronization remain.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd.
Test: face a fixed landmark, hold Q or E, then repeatedly raise/lower the weapon without moving the mouse. The camera should retain its forward direction. Test both sides, then look up/down and check the grip.
F7 custom/native comparison. Ctrl+F9 support-hand solver comparison. No batch menus.
Collect-Logs.cmd collects diagnostics. Local checks passed; Windows compilation and gameplay are not available here.
