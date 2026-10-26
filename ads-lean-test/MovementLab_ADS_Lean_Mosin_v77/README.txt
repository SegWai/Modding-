MovementLab lean test v77 — transition eye-position isolation

Based on v76. During raising, eye correction waits for native raise completion and enters over 0.10s. During lowering it releases the last head-local correction over 0.10s rather than following the moving rifle. Full raised framing and native look direction retained.
Pose graph, animation smoothing, grip and ADS code unchanged. This is a camera-only test; visual result is unverified.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd.
Hold Q and repeatedly raise/lower; repeat on E. Check the brief obstruction and forward direction. Then look up/down while fully raised and inspect grip.
F7 custom/native; Ctrl+F9 support-hand solver comparison. Collect-Logs.cmd collects diagnostics.
Local checks only; native compilation and visual playback require Windows DayZ.
