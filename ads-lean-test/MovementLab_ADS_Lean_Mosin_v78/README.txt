MovementLab lean test v78 — native lean timing and short pose handoff

Lean visual amount follows the native interpolated movement state directly. Removes the extra 0.10s time-constant filter; native lean smoothing is retained, including reversals.
Custom raise/lower smoothstep: 0.08s instead of 0.36s. Standing/walking pose blend: 0.08s instead of 0.20s. Native weapon raise/fire eligibility is unchanged.
V77 camera code (including its separate 0.10s camera-only correction), full graph, authored poses and native/custom grip timings are unchanged.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd.
Test raise/lower, Q/E from neutral, direct Q-to-E reversals, and standing-to-walking in both views. F7 compares custom/native. Ctrl+F9 compares added support-hand solver. Collect-Logs.cmd collects diagnostics.
Only runtime essentials included. Local checks passed; native compilation, exact timing and visual playback require Windows DayZ.
