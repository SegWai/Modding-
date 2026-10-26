MovementLab lean test v80 — custom aiming leans as default

For Mosin and AK74, stock raised-weapon lean chains are bypassed in standing idle/walk and crouch idle/walk, including the custom raise/lower blend. The optimized custom branch uses the unleaned raised base plus our existing custom pose. F7/F8 can no longer disable custom posing or enable native comparisons. Player and NPC share this path.
V79 camera fix, authored poses, grip solver, native lean interpolation and short 0.08s blends are retained. Lowered/non-aiming lean and other weapons remain native. Original installed DayZ assets are not deleted.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd. Test standing/walking/crouch Q/E, raised-only and actual ADS, and transitions in both views. Ctrl+F9 still compares the support-hand solver. Collect-Logs.cmd collects diagnostics.
Rollback: keep v79 in its own folder and launch that version to restore the previous setup. Exact backup:
https://raw.githubusercontent.com/SegWai/Modding-/bbe890c/artifacts/MovementLab_ADS_Lean_Mosin_v79.zip
Local graph/source/package checks only; native compilation and visual playback require Windows DayZ.
