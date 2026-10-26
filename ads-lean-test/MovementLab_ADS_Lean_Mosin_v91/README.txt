MovementLab lean test v91 — moving hold 10cm lower

Both hand/weapon targets are now 10cm lower while moving left or right, compared with 5cm in v90. Stationary lowering remains 5cm. Uses existing 0.08s movement pose blend to interpolate between these amounts; target and source-restoration offsets match at every blend value.
Same arms-only solve as v90. First-person crouch-style view, body/head/legs, aim rotation, camera and timing are unchanged.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Check both moving directions, stop/start, grip and aim up/down. Collect-Logs.cmd collects diagnostics.
Local graph/source/package checks only; exact native visual lowering requires Windows DayZ testing.
