Standing Jog Two Levels v1 — separate test based on walking v3.
Close DayZ, extract entire ZIP, run Launch-Movement-Test.cmd.
In standing jogging mode, scroll up for130%, down for100% (default).
Ctrl still toggles walking/jogging. Jog choice persists across mode/stance changes.
Walking retains its separate ~85/100/120 levels and crouch-exit walk reset.
Crouch retains its independent six wheel levels and entry defaults.
Shift still selects full sprint; wheel is ignored while Shift is held.
Only six healthy standing jogging clips have39FPS variants for130% pace.
Native jogging clips30FPS are preserved. Jogging parts of start/stop/sprint
transitions inherit saved jog pace. Full sprint clips are untouched.
Existing movement logic and timers unchanged. No F8 or jogging/walking UI messages.
Diagnostics go to script logs. If unchanged, close DayZ, run Collect-Logs.cmd,
and attach MovementLab-Jogging-v1-Logs.zip.
Native animation/travel speed and Windows preparation require local testing.
