MovementLab Ctrl Modes v8 - permanent responsive body rotation / v7 crouch rules

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

The preferred responsive body rotation is enabled from startup. The old F8
comparison flag and handler have been removed; F8 has no custom movement effect.
This is the former second/F8-on setting: walk/jog heading multiplier 1.6.
Direction multiplier remains 2.5. Sprint settings are unchanged.
F7 still retains the separate whole-profile vanilla comparison.

Standing controls and the v7 crouch rules are unchanged:
- Tap Ctrl while standing to toggle walk/jog; hold Shift for standing sprint.
- Crouch without Shift: slow crouch.
- Crouch with Shift + direction: original native DayZ fast crouch.
- Stand from active fast crouch: jogging until Ctrl selects walk. Release
  that existing Shift hold before pressing it again for standing sprint.
- Stand from slow crouch: preserve the previous standing walk/jog mode.
- Releasing Shift while still crouched returns to slow crouch; its exit
  preserves the previous standing mode. Shift alone does not move you.

All World/crouch/start/stop methods are byte-identical to tested v7. Actual
translated filter checks compare all five output values against v7's preferred
responsive setting across braking/stamina/profile states and verify F8 has
no effect. No animation clip or playback speed changes. Native in-game
compilation/animation/physics testing remains local. Logs: Profiles/MovementLogic.
Historical v4 and v7 packages remain unchanged.
