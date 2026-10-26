MovementLab lean test v76 — raised-camera attachment timing

Based on v75. Preserves native view direction, v71 poses, smoothing and grip logic.
Camera position stays attached to the head during raise/lower; switches to the v75 position-only wrist attachment after the native raise completes. Both paths use the same calculated eye position. No added filtering or timing changes.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd.
Test repeated raise/lower while holding Q, then E. Check the brief top-left fragment and forward direction. Then check settled grip while looking up/down.
F7 custom/native; Ctrl+F9 support-hand solver comparison. Collect-Logs.cmd collects diagnostics.
Local checks only; native compilation and gameplay need Windows DayZ.
