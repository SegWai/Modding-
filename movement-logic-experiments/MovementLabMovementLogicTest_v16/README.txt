MovementLab v16 - Heavier moving reversals, rapid-input protection

Close DayZ, keep Steam running, extract this ZIP into a fresh folder,
and run Launch-Movement-Test.cmd. No packing or animation import needed.

Test A -> D -> A and W -> S -> W, including rapid taps and overlapping keys.
F8 toggles ONLY the moving-reversal addition. F7 retains heavier/vanilla.
Test standing with empty hands; deliberate Ctrl/manual walking bypasses it.

Each reversal now completes its committed direction before accepting another.
Extra presses cannot restart the native brace or change direction mid-blend.
After the protected handoff, current input determines the next reversal;
individual taps are not queued for playback later. Short release gaps below
0.10 seconds are tolerated. A sustained release cancels; UI/death/falling and
other safety exclusions still cancel immediately. This slightly delays a
complete release during the reversal only.

Recovery is 0.62 seconds (v15 was 0.50), with a heavier initial slowdown and
slower push-off. The native handoff is protected for 0.14 seconds.
Movement stays continuous; no scheduled stationary hold or clip-rate freeze.
Ordinary v11 startup and braking methods/timings are unchanged.

Checks exercise actual translated methods at 30/60/144 FPS with alternating
keys, overlapping opposite keys and short release gaps. This is a mocked SDK
check, not an Enforce compile or native animation test. Confirm stability in
DayZ; logs are under Profiles/MovementLogic, labelled [MovementLab v16].
V11 and v15 remain available unchanged.
