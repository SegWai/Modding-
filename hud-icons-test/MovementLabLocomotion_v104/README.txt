MovementLab v104 — crawling handoff visibility/readiness correction

Extract into a NEW folder, launch, break the zombie's leg, let it crawl fully,
then kill it. Close DayZ and run Collect-Logs.cmd; send MovementLab-Corpse-v104-Logs.zip
and say whether it flashed upright and whether the ground-level body had ragdoll.

The latest v103 crawl log DID activate ragdoll, but at pelvis height0.537m while
still lowering. v104 requires native prone stance, pelvis below0.35m, head below
0.5m, and a stable low pose for100ms. It allows up to2s to settle. A standing
replacement is never a crawler fallback. Failure retains the original corpse.

The original infected's simulation freezes immediately after confirmed death,
preventing its native fall animation during initialization. The replacement stays
hidden from construction and reasserts that state in POSTFRAME until reveal.
Cleanup restores the source on failure. Momentum and 5s respawn are retained.

This is a focused crawl-transition correction, NOT exact-frame full-pose transfer.
The raised-arm approximation in v103 still does not meet that requirement. A
separate captured-pose animation-graph bridge is under investigation. Native v104
compilation, stable prone thresholds and the visible result require your game run.
