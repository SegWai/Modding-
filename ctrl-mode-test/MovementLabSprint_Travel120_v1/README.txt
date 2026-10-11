Sprint Travel120 v1 — physical movement experiment from corrected scroll v2.
Enter scroll sprint, then scroll up once for level3 (target20% extra ground travel).
Native sprint animation retained to isolate actual speed from clip-rate changes.
Level2 native100; down fromlevel2 returns jogging100 exactly as corrected v2.
Uses documented OnPhysMove callback with collision query, leaving height untouched.
Boost only on grounded, unattached, fully achieved local standing sprint with
directional input. Disabled during braking; native stop timers retained.
No walking/jogging/crouch clip changes. Actual speed requires in-game testing.
Native animation pace remains100, so foot sliding may be visible in this diagnostic.
Close DayZ, extract entire ZIP and run Launch-Movement-Test.cmd.
If ineffective/error, close DayZ, run Collect-Logs.cmd and attach generated ZIP.
