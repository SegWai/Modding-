Mosin lean v16 — reverse the left-lean head roll

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Vanilla Mosin. No batch menu.

The existing left-lean Head Z rotation is reversed in all four pose branches: standing idle/walking and crouched idle/walking. This changes a +13-degree graph roll to -13 degrees (26 degrees difference from v15 at full left lean). Both player and NPC use these branches. This targets the requested anatomical-left head angle directly. The forward 5-degree nod remains. Right-lean head, restored stationary legs, moving/crouched legs, arms, hands, weapon roll and working NPC controller are unchanged.

F10 pauses/resumes the NPC for inspection. Check its left lean, then your own Q left lean while aiming. F8 enables third-person raised-Mosin inspection. F6 retains the native ADS head-tilt comparison from v15; suppression is enabled by default. F7 compares full native/custom lean. F9 records measurements.

Local checks verify the four sign reversals and unchanged remaining pose/control code. Native appearance still requires an in-game test. If wrong, send a screenshot of the left lean and the Collect-Logs.cmd ZIP (v16 label).
