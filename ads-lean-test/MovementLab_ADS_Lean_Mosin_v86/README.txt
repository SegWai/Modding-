MovementLab lean test v86 — isolate extra left transition solver

Diagnostic comparison based on v85. Bypasses only the v83 partial-left aim constraint, whose weight rises at lean 0..0.125, stays on until 0.875, then falls to zero at full lean.
All other blend stages, v85 camera framing, authored poses, native lean timing and short raise blends are unchanged. The disabled constraint already had zero weight at neutral/full left and everywhere on the right, so those endpoints/paths are preserved.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd.
Test: face a fixed landmark and keep the mouse still. Raise neutral for one second, hold Q for one second, release for one second; repeat three times, then repeat with E. Record whether the extra dip/tilt/catch-up stages disappear compared with v85. Collect-Logs.cmd collects diagnostics.
Do not change Ctrl+F9 support-solver setting during this comparison. V85 remains a separate rollback package.
Local source/graph checks passed; this isolates a suspected cause, not a confirmed native fix. Native compilation/playback require Windows DayZ.
