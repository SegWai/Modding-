MovementLab v102 — measured movement priority and gravity-preserving transfer

Extract into a NEW folder and launch normally. Kill the infected while standing,
walking and running. Note the corpse's horizontal travel and initial pose.
Close DayZ, run Collect-Logs.cmd and send MovementLab-Corpse-v102-Logs.zip.

The v101 logs show successful initialized ragdolls but captured speeds of only
0 and 0.215m/s. v102 prefers recent world-displacement measurements over the
AI controller's reported velocity. An 80ms measurement window reduces zero/spike
samples between native AI position updates. Native velocity is only a fallback.
Both measurements and the selected source are logged.

Only horizontal momentum is corrected. Natural vertical settling/gravity is
preserved; the 23Ns vertical correction seen in v101 is removed. Transfers once,
not a continuous push. Pelvis travel is logged at approximately 100 and 300ms
after reveal to check actual articulated follow-through, not just an impulse call.
The v101 pose warmup, rollback and five-second respawn are retained. Existing
player and human-NPC code is unchanged. Native motion still needs your game test.
