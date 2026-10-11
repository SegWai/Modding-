Standing Walk Three Levels v3 — separate version; no F8 toggle.
Close DayZ, extract entire ZIP, run Launch-Movement-Test.cmd.
Ctrl selects walk/jog as before; Shift still selects sprint.
While standing in walking mode: scroll up/down selects levels1..3.
Level1:~85% (26 FPS=86.67%), default and reset on leaving crouch.
Level2:100% original normal walking (30 FPS).
Level3:120% walking (36 FPS).
Crouch retains its own six wheel levels and defaults; standing/crouch gait
rules and previous acceleration/braking/turning/strafe logic are retained.
Leaving crouch resets the WALK SPEED selection to~85%; it does not force a
previously jogging character into walk mode. Walking portions of transitions
also use the selected rate. Jog/sprint clips remain unchanged.
F7 vanilla comparison remains; F8 comparison removed.
Original Windows files are read only. In-game speed/foot contact require test.

V3 selects the complete healthy upright movement branch, as with crouch.
Walking level messages removed; diagnostics are written only to script logs.
If speed remains unchanged, close DayZ and run Collect-Logs.cmd, then send ZIP.
