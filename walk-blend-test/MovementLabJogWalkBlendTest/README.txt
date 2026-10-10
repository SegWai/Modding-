MovementLab isolated jog-to-walk velocity blend v1

Close DayZ, keep Steam running, extract this WHOLE ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No Addon Builder or animation import needed.
Do not combine it with the earlier test mods; its launcher loads only this one.
The launcher uses D:\SteamLibrary\steamapps\common\DayZ\DayZDiag_x64.exe.

TEST:
1. Hold W and let the character reach normal jogging.
2. Keep W held and HOLD Ctrl to enter walking (ordinary DayZ controls).
3. The first part of the transition keeps more momentum, then eases down
   to ordinary walking over 0.45 seconds. Keep Ctrl held to keep walking.
4. Release Ctrl to return to native jogging.
5. F7 switches this single change off/on for comparison with vanilla.
   Release Ctrl and jog again before repeating each comparison.

This is a standalone experiment. It does not include the Ctrl toggle, v11
walking startup, heavy acceleration, scripted stopping tails or reversal logic.
Only the jog-to-walk handoff requests a temporary speed blend. Direction,
normal walk/jog/sprint, stopping and other movement remain native. Releasing
movement, changing direction, pressing Shift, aiming, gestures, other stances
or opening a menu cancels the blend. Current stable Ctrl Modes v2 is untouched.

The script changes DayZ gait input (2 jogging to 1 walking), not a measured
m/s value or an independent walk-clip velocity. The engine owns the resulting
physical velocity and animation blend; no frame freezing or entity movement.
Smoothstep has zero slope at both ends to avoid a sharp speed handoff.

Translated actual-hook mock checks passed at 30/60/144 FPS across forward,
backward, lateral and diagonal input, including cancellations and handoff.
Native Enforce compilation, visual blending and physical speed need your
in-game test. Logs are in Profiles\JogWalkBlend.
