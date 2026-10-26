MovementLab lean test v81 — shared pose/camera transition timing

Based on v80. Removes the camera-only wait for raise completion and its following 0.10s blend. Camera eye correction now uses the same current pose gate/lean weight as the custom arms.
Native head attachment and look direction retained. Full raised eye target, custom-only Mosin/AK74 aiming graph, grip logic and fast 0.08s transitions unchanged. No default raised-lean comparison restored.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Test repeated raise/lower while leaning both sides, rapid left/right changes, and fully raised look up/down. Inspect for the brief enlarged/high rifle. Collect-Logs.cmd collects diagnostics.
Rollback backups v79 and v80 remain separately available. Local source/package checks passed; native compilation and visual result require Windows DayZ.
