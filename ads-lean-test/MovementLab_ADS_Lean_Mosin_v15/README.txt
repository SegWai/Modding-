Mosin lean v15 — native ADS head-tilt correction

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd directly.
Project root F:\DayZProjects. Vanilla Mosin only. No launcher menu.

The official HumanCommandWeapons.SetADS(bool) API explicitly controls head tilt to optics. Earlier code enabled it on the NPC and native player HandleADS enabled it for the player. V15 suppresses this native tilt while custom lean is active, for both actors, after native CommandHandler processing. It leaves the player's camera/sight flags alone. On neutral lean, native comparison or custom lean exit it restores the expected ADS head-tilt request. V14's empirical extra 12-degree roll pass is removed; the 5-degree forward head nod remains. The authored neck/head alignment, legs, hands, weapon cant and NPC controller are otherwise unchanged.

F6 toggles ONLY the automatic ADS head-tilt suppression during custom lean, on both actors. Correction is ON by default (native head tilt OFF). Use F10 to pause the NPC first, then F6 to compare the same pose. This is an in-game comparison, not a batch choice.
F7 compares full native/custom lean. F8 enables raised-Mosin third-person inspection.
F9 records player/NPC measurements. F10 pauses/resumes NPC movement.

Test both directions on the NPC and your character. Confirm the head is upright and nods slightly forward while leaning, and ADS camera/sight alignment still behaves correctly. The v14 restored stationary legs and the walking/crouched legs are unchanged. Source/API and packed-file checks cannot verify the final native appearance or ADS camera alignment. If wrong, close DayZ, run Collect-Logs.cmd, and send the ZIP with a screenshot stating which F6 mode is shown.
