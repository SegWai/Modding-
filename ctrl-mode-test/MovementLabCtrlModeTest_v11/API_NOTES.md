# Ctrl Modes v11 lateral reversal resistance on v10

New World tracker runs after mode/start handling and before base CommandHandler.
It is eligible only for standing local offline jogging, excluding startup,
braking, aiming, gestures, UI and invalid timesteps. Exclusive lateral sign is
remembered through 0.18s neutral/both-held gaps. Opposite input at achieved gait
>=1.75, or during an existing resistance window, sets a 0.50s resistance timer.
Same-side input does not refresh the timer. Repeated opposite inputs refresh it
without any command/clip transition. Decay is smoothstep(timer/0.50).

Only mission SetDirectionFilterModifier changes: custom direction multiplier
2.5 + 4.5 * resistance. Body heading remains 1.6 and sprint direction/heading
and run-sprint filters remain v10. Walking/sprint/crouch/exclusions reset the
tracker. The tracker does not override speed/angle, freeze a frame or alter
position. Existing startup, crouch and brake logic and their timings remain.
This intentionally avoids earlier reversal experiments' command ownership and
clip restart problems. Actual native paths and visual behavior are not proven.

Actual translated script checks at 30/60/144 FPS in both callback orders cover
reversal trigger, diagonal and spam inputs, no startup/brake/angle ownership
changes, smooth decay and walking/sprint/crouch exclusions. Existing standing,
crouch, Ctrl transition and original-v11 full-stop comparisons pass. Actual
filter methods compare to v10 for no resistance/vanilla, and verify only the
direction timeout differs with resistance 0/.5/1 across braking/stamina states.
Native Enforce compilation, animation stability and physics testing are local.
This test is distinct from the historical original Movement Logic v11.
