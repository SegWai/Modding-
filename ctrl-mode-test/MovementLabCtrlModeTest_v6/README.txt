MovementLab Ctrl Modes v6 - restore native fast crouch / standing jog return

Close DayZ, keep Steam running, extract the WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing/import needed.

FIX FROM V5:
V5 forced gait 2 while crouched Shift was held. The native crouch graph has
its fast blend above gait 2, so that override suppressed the fast crouch.
V6 removes the crouch speed cap entirely. DayZ owns crouched movement and
its normal Shift behavior, as in the approved v4 version.

TEST:
- Select standing walking with Ctrl, then crouch.
- Hold a direction + Shift: the original fast crouch should work again.
- Release Shift while crouched: ordinary native crouch movement.
- Stand up: selects standing jogging, even if Shift was released first.
- Tap Ctrl while standing to select walking again.
- Stand while still holding Shift: normal standing sprint; release Shift
  to return to jogging. Releasing Shift and standing in the same frame also
  selects jogging without holding the crouched fast speed.
- Shift without movement does not generate movement.

Ctrl while crouched uses native crouch input and does not toggle saved standing
mode. Release and tap Ctrl again while standing to select walking. All native
crouch direction/stance/weapon restrictions still apply; no new clips or
playback rates are added. The script leaves both crouch speed and angle
ownership disabled, including during standing-brake cancellation.

Standing controls, approved v4 direction fixes and existing timers are retained.
F8 still compares original/responsive BODY TURNING ONLY. Direction delay stays
identical in both settings. F7 still compares the whole profile with vanilla.
Approved stable v4 is unchanged; this is a separate correction to test.
The discarded standalone walk-blend experiment is not included.

Actual translated tests pass at 30/60/144 FPS, both callback orders. V5 fails
the new crouch ownership check; v6 passes. Native-input mock fallback verifies
no gait cap, stance/Shift release orders and idle input. Standing startup,
stopping and rear-diagonal regressions still pass, and the filter method is
identical to approved v4. This does not measure native velocity or clip frames.
Native Enforce compilation and the fast crouch animation need the game test.
Logs: Profiles/MovementLogic.
