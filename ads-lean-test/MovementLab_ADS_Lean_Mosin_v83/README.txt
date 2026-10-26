MovementLab lean test v83 — standing Q transition aim constraint

Based on v81, reversing the unsuccessful v82 balance change. A native weapon aim/primary/support-chain solve now runs after custom posing only during partial standing-left lean. It targets native look yaw/pitch and the existing roll target, with short spatial ramps at both ends. It is disabled at exact neutral/full lean, right lean, walking and crouching.
This changes the transition arm pose intentionally; endpoint poses, native lean timing, custom-only raised lean routing and camera code are unchanged. No native default lean animation is reintroduced.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd. Raise weapon, press/hold/release Q repeatedly and inspect rifle orientation throughout. Also test aiming up/down while transitioning, final grip and full lean distance. Collect-Logs.cmd collects diagnostics.
Local source/graph/package checks only; native IK compilation and visual behavior require Windows DayZ. Previous packages remain rollback options.
