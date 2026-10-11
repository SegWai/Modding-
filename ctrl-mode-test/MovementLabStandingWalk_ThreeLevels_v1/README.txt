Standing Walk Three Levels v1 — separate version; no F8 toggle.
Close DayZ, extract entire ZIP, run Launch-Movement-Test.cmd.
Ctrl selects walk/jog as before; Shift still selects sprint.
While standing in walking mode: scroll up/down selects levels1..3.
Level1:70% (21 FPS), default and reset on leaving crouch.
Level2:~85% target; native integer FPS rounds to26/30=86.67%.
Level3:100% original normal walking (30 FPS).
Crouch retains its own six wheel levels and defaults; standing/crouch gait
rules and previous acceleration/braking/turning/strafe logic are retained.
Leaving crouch resets the WALK SPEED selection to70%; it does not force a
previously jogging character into walk mode. Walking portions of transitions
also use the selected rate. Jog/sprint clips remain unchanged.
F7 vanilla comparison remains; F8 comparison removed.
Original Windows files are read only. In-game speed/foot contact require test.
