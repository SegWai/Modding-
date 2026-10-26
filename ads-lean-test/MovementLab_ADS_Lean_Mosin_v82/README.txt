MovementLab lean test v82 — standing lean balance interpolation

Removes duplicate lean-amplitude weighting from the outer standing balance blend. The inner left/right balance blends already apply signed lean amplitude. Their correction now progresses with the base pose instead of lagging quadratically.
Neutral/full-lean transforms unchanged; partial standing transition trajectory changes intentionally. Same correction for both directions. Camera code, fast raise/gait timing, native lean amount, walking/crouch routing and custom-only raised leans retained.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd. Test raised Q entry/exit and left/right reversal. Check rifle roll throughout, then compare full lean distance and pose. Collect-Logs.cmd collects diagnostics.
Local graph/source checks only; native compilation and visual outcome require Windows DayZ. Previous builds remain separate rollback packages.
