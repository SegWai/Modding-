MovementLab walking-first controls v1 (based on stable v11)

Close DayZ, keep Steam running, extract this entire ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing or animation import needed.
V11 remains unchanged. This launcher loads only the included controls PBO.

Controls, standing in the offline test:
- WASD: walk by default, without Ctrl.
- Hold Shift once while moving: jog.
- Double-tap Shift within 0.30 seconds while moving: latch sprint.
  You may release Shift after the second tap; sprint lasts until you release
  movement. Releasing movement clears sprint and the double-tap history.
- Release Shift during ordinary jogging while continuing WASD: ease to walk.
- Release movement: settle in the last direction, then idle.
- F7: switch this controls/heavy profile off for vanilla, or back on.
Ctrl still forces walking and clears sprint. Native direction/stamina/stance
limits remain; the engine may cap sprint in a direction it does not support.

Standing startup requests walking in the first command tick, even with Shift.
It leads into jogging, then sprint if double-tapped. Releasing movement follows
achieved gait, avoiding a long sprint stop after an unachieved sprint request.
Near/full sprint uses the v11 stop budget and jog->walk phases. Jogging has
the v11 0.42-second settle (backward 0.18); walking has a short 0.14-second stop.
A/D/S and diagonal stops retain their movement direction.
Repressing a movement key during a stop starts walking, with Shift deciding
whether it then speeds up. Opposing held keys with zero net direction stop.

Test each control and stops forward/back/sideways/diagonally. Check that Shift
held once only jogs and two separate slow presses do not latch sprint.
Logs: Profiles/MovementLogic. Native DayZ chooses/blends all animations.
There is no reversal experiment, script-command handoff, frame hold or direct
position change. Crouching/prone, aiming/gestures, menus, death, falling and
multiplayer are excluded; exclusions restore native controls.

Actual translated controller/PlayerBase checks passed at 30/60/144 FPS with
a mocked SDK. This is not native Enforce compilation or animation verification;
those still need the local DayZ test. No DayZ game assets are included.
