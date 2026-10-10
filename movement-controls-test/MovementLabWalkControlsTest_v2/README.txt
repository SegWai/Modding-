MovementLab walking-first controls v2 - approved v11 movement feel

Close DayZ, keep Steam running, extract into a fresh folder, and run
Launch-Movement-Test.cmd. No packing/import needed. Original v11 is unchanged.

WASD walks. Hold Shift to jog. Double-tap Shift within 0.30 seconds while
moving to latch sprint; releasing movement clears sprint. Release a single
held Shift while jogging to return to walking. F7 switches to/from vanilla.
Ctrl forces walking and clears sprint. Native direction/stamina limits apply.

Restored/improved in this build:
- Walk from the first movement tick, never an initial jogging frame.
- V11 startup lead-in: walk ~0.10s, reach jog over ~0.18s, allow sprint only
  after the ~0.35s lead-in and an achieved jogging gait. A fast double Shift
  cannot interpolate directly from walk toward full sprint.
- Walk->jog and jog->sprint are distinct smooth request stages. Stepping down
  from an achieved sprint toward walking also goes through jogging first.
- Repressing movement during a stop retargets from its current moving gait
  rather than snapping straight to a new walking pose. Once stopped, starts
  again from walking.
- Stops use achieved gait/exposure, not a requested but unreached sprint.
  A barely started sprint gets at least a jogging-size settle, rather than
  an unusually shorter stop. Full-sprint stop budget remains the v11 value.
- Same full-sprint stopping budget forward, diagonally and sideways.
  Longer jogging, shorter walking finish within that budget.
- A/D stops finish with sideways walking; S jogging uses the much shorter
  backward walk finish (~0.18s versus ~0.42s lateral jogging settle).
- Walking has its short ~0.14s settle. Net key direction is retained on
  stops even if opposing keys were simultaneously held with another key.
- Original heavy acceleration/direction/turn filters retained.

Test default walk, single Shift hold, quick double Shift, stops in each
direction, very brief sprint requests, and movement resumed mid-stop.
No rejected reversal logic, scripted command, manual frame hold or graph
animation writes are added. Native DayZ owns all animation/translation.

Actual translated controller checks pass at 30/60/144 FPS with a mocked SDK.
This is not an Enforce compile or a native animation/blending test; confirm
those locally. Controls apply standing; aiming/gestures/crouch/prone/menus,
falling/death and multiplayer restore native controls. Logs: Profiles/MovementLogic.
V11 and walking-first v1 remain available unchanged.
