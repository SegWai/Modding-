MovementLab lean test v84 — selective smoothing

Standing/crouched lean entry and exit, raised or lowered: same-duration smoothstep visual curve with softer endpoints. Raising/lowering while leaned retains the short 0.08s smoothstep pose blend and shared camera weight.
Direct Q-to-E and E-to-Q reversals bypass added lean easing and follow native movement lean values. Mapped keyboard/gamepad actions detect reversals before the native value crosses zero; the demo supplies its direction to the same helper. No native inputs or firing rules are modified.
Graph, authored poses, v83 standing-left transition aim constraint, custom-only raised branches and camera code unchanged. Endpoint distances remain the same; partial entry/exit trajectories change intentionally.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Test entry/exit then direct Q/E reversals while standing/crouched, lowered/raised/ADS. Test raise/lower while leaned. Collect-Logs.cmd collects diagnostics.
Local source and reversal-state tests passed; native compilation, toggle-lean/controller edge cases and visual behavior need Windows DayZ testing.
