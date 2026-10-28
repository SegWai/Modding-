AMBIDEXTROUS LEAN - EXPERIMENTAL V6

V5 screenshot shows remaining sideways rifle roll and mismatched support arm.
V6 adds a bounded grip calibration rather than assuming the right-hand weapon
profile has the same orientation on the left hand.

Raise AK74, aim level and stand centred. Press side button and hold aim steady
for about2seconds on first use of that pose. It measures the left gun frame,
briefly probes5degrees of native roll to determine the actual direction, applies
ONE measured roll correction, then solves the RIGHT support arm to the original
under-barrel wrist location stored in weapon-local coordinates. The left trigger
hand and original mirrored body pose remain unchanged. An unreachable arm target
is rejected, not stretched. Wrist orientation and limb lengths are preserved by
that support solve. No saved JSONs changed; original leaning mod186 preserved.

Each cached weapon/stance/gait/lean/ADS context does this once. It stops after
four bounded stages, never repeatedly recaptures corrected arms or continuously
adjusts pose. New contexts need level aim briefly; moving mouse pauses setup.
Native left/right weapon-profile limitations, gait sway or remaining wrist/hand
fit may still need work. Lowered/reload/interact animations remain right-handed.

Same mouse binding, automatic spawn neutral setup, default third-person camera,
no NPCs. If still wrong, send Collect-Logs AND screenshot/recording: new logs show
measured roll response/correction and whether support target was reachable.
Offline math/source/graph/PBO checks do not prove native compilation or visible
contact; V6 native hand fit, gun roll, ADS/firing and FPS have NOT been run here.
