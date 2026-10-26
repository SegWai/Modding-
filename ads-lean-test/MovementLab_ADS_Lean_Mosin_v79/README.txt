MovementLab lean test v79 — stable native camera parent

Based on v78. Camera always keeps the native head attachment; no wrist attachment or head/wrist switching. Existing eye-target calculation, camera-only raise envelope and native look direction retained.
Pose graph, grip behavior, native lean timing and short 0.08s transition blends unchanged.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd.
Hold lean and raise, then remain raised for several seconds. Repeat both sides and look up/down. Check for the one-frame enlarged/high rifle and any camera/arm tracking regression.
F7 custom/native, Ctrl+F9 support-hand solver comparison. Collect-Logs.cmd collects diagnostics.
This isolates camera parenting as a possible cause; native render behavior and final visual fix have not been verified here. Local source/package checks only.
