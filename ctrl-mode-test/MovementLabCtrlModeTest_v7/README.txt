MovementLab Ctrl Modes v7 - four crouch rules rebuilt directly from stable v4

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

RULES:
1. Crouch without Shift: slow crouch, regardless of saved standing mode.
2. Crouch with Shift + direction: ORIGINAL native DayZ fast crouch. The slow
   speed override is released; fast crouch is not capped to a guessed gait.
3. Stand up FROM ACTIVE FAST CROUCH: selects persistent standing JOG mode.
   The Shift hold already used for fast crouch is consumed on this exit, so
   it does not become a full upright sprint. Release and press Shift again
   to sprint normally. Tap Ctrl to select standing walk as before.
4. Stand up FROM SLOW CROUCH: preserves the previous standing mode. If it was
   walking, it stays walking until you tap Ctrl; jogging stays jogging too.

TEST THE DISTINCTION:
- Stand walking -> crouch -> W without Shift -> stand: walking.
- Stand walking -> crouch -> W+Shift -> stand WHILE HOLDING Shift: jogging.
- In that jog, release Shift: still jogging. New Shift press: normal sprint.
- Fast crouch -> release Shift while STILL CROUCHED -> slow crouch -> stand:
  previous standing mode is preserved. Fast crouch does not latch forever.
- Shift without direction is not fast moving crouch and does not select jog
  on standing. Release Shift and standing simultaneously after fast crouch
  selects jog from the last crouched moving state.

Normal standing behavior is the approved v4 behavior: Ctrl walk/jog toggle,
held Shift sprint, original speed curves and timings, direction fix and F8
body-only rotation comparison. The only standing exception is the fast-crouch
exit described in rule 3. F8 starts with the same original turning as v4.
F7 retains the whole-profile vanilla comparison. Ctrl presses while crouched
are sampled but do not change the saved standing mode; tap anew when standing.
No crouch clip, frame-rate or direct position changes are made.

This was copied from v4, NOT v5 or v6. Stable v4 is unchanged and remains the
approved fallback. The previous crouch experiments are not incorporated.
Native crouch direction/weapon/stance restrictions still apply.

Actual translated command/mission tests pass at 30/60/144 FPS in both callback
orders for all four rules, prior walk/jog modes and eight direction masks.
Tests cover native fast input ownership, slow crouch gait, Shift release before,
after and simultaneous with standing, idle Shift, standing-brake interruption,
Ctrl switching after fast exit, and disabled/prone exclusions. Standing v4
regressions and v11 stopping comparisons pass; filter code is identical to v4.
Native Enforce compilation, physical velocity and animation clips cannot be
verified here and require your local game test. Logs: Profiles/MovementLogic.
