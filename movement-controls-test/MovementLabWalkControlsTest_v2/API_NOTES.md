# Walking-first controls v2

Extends walking-first v1 using the user's accepted v11 behavior as the target;
the original v11 package/source remain byte-identical. Native command-level
speed overrides and mission filter modifiers remain, with one gait owner.
No v12-v17 reversal experiments are reintroduced.

Main correction: separate desired gait from the next interpolation stage.
A sprint request while walking first targets gait 2, then gait 3 only after
jogging is requested, achieved gait >=1.75 and the initial lead-in >=0.35s.
A walk request above gait 2 first targets jogging. From idle the first frame
requests walking, with a ~0.10s lead-in then ~0.18s walk/jog blend. Native
sprint filters still govern observed pace and pose blending.

Resuming during a coast starts interpolation at min(current request, achieved
gait) instead of resetting gait to 1. An actual idle start still starts at 1.
Stop curves preserve v11's full-sprint budget/phase distribution, side walk
finish and short backward finish. A near-jog sprint's old exposure formula
could yield a stop shorter than ordinary jogging; its budget now has a jog
floor (0.42s, or 0.18s backwards). Full sustained sprint remains 1.15s.
Walking settle remains v1's added 0.14s. Effective key masks now use net
forward/side components, avoiding false forward/back flags from opposing keys.

Controls unchanged: WASD walks, Shift hold jogs, double Shift <=0.30s latches
sprint until movement release. Ctrl forces walk/clears latch; F7 compares
with native controls. Native caps and stance exclusions remain unchanged.

Tests execute actual mechanically translated controller/integration methods
at 30/60/144 FPS with a mock SDK. Added assertions cover explicit jog before
sprint, achieved-gait stop budgets, equal full sprint deadlines across forward/
diagonal/side inputs, smooth coast retargeting, backward tail length, and
opposing-key overlap with a net lateral direction. Tests do not compile
Enforce, simulate native graph clocks, collision or verify native visuals.
