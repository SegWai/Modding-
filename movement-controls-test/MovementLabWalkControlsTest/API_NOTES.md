# Walking-first controls v1

Built separately from stable v11; its original source and ZIP are untouched.
Mission spawn, native direction/turn/inertia filter values and F7 comparison
are retained. PlayerBase now owns default gait, Shift detection, acceleration
and release stops in one native-command hook. The old mission brake controller
is removed to avoid competing overrides. The mission accelerates the native
run/sprint filter during stopping as in v11.

Shift is sampled through UATurbo.LocalValue rising edges, not LocalPress,
so a held key never counts as repeated taps. Two presses within 0.30 seconds
while moving latch sprint until movement release. A single held Shift requests
jogging; releasing it requests walking. Explicit Ctrl walking clears the latch.
Startup's first tick requests gait 1 before the base handler, irrespective of
Shift or a longer supported frame. Then it eases toward gait 2 or 3.

Stop origin is min(achieved native gait, previous requested gait), avoiding
inflating a brief sprint tap. V11 sprint exposure/budget and near-full sprint
phase curve are retained. Jog settles in 0.42s, backward jog in 0.18s;
walk settles in 0.14s. Lateral tails keep walking; backward tails are short.
Persistent speed ownership primes idle at 0 and avoids native jogging leakage.
Only braking overrides the movement angle; normal movement remains native.

No HumanCommandScript, direct translation, graph writes, clock freezes or
manual brace requests. Native stance/direction/sprint limits are unchanged.
Short early-return eligibility checks avoid the earlier formula-complexity
failure. Override argument names match CommandHandler's native prototype.

Tests translate the actual controller and PlayerBase integration into C++
with mocks and verify 30/60/144 FPS, walk default, jog hold, double-tap/latch,
slow taps, release reset, staged direction-preserving stops, premature sprint
release, braking interruption, startup first tick and exclusions. They do not
compile Enforce or model native pose blending/collisions. Local testing is
required for native compilation and visuals.
