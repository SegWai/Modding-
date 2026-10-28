AMBIDEXTROUS LEAN - EXPERIMENTAL V8

V7 only converted wrist orientation and placed the publisher at the left wrist.
It omitted the native hand-to-gun translation and did not reflect the gun frame.
V8 solves the full rigid hand-to-sight transform from the original native pose,
reflects the desired sight position/forward/up about the same chest plane used
for the arms, and inverts the full profile to calculate the required anchor.
The anchor follows the left wrist using a cached local rotation AND translation.
No fixed guessed roll angle, continuous probing or arm stretching.

All four approved pose JSON files and mirrored visible arm/hand/finger solver
are unchanged. Same mouse-side button, native camera distance/height, no NPCs.
Extract to a fresh folder; do not load both the saved lean mod and this fork.
Use Launch-Mosin-Lean-Test.cmd. Lowered/reload actions remain native right-handed.

Offline checks verify full-profile inverse/reflection and runtime packaging.
Native compilation, virtual Weapon-helper publishing, rendered attachment,
firing/ADS and tracking are NOT verified here. The sight accessor may differ
from the renderer attachment; this remains an experimental native integration.
Logs now identify MLASHOULDER8 and include the nonzero profile offset so we can
verify this correction is active. Collect-Logs.ps1 collects the test logs.
