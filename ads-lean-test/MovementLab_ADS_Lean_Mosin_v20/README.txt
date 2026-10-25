Mosin lean v20 — right-lean head exposure test

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd directly.
Project root F:\DayZProjects. Existing v19 shooting range is retained.

Right lean now bends the neck 10 degrees toward anatomical left and shifts its head subtree 2.5cm toward anatomical left plus 1cm upward. This moves the head centre beside the rifle rather than only rotating the head about its own pivot. The neck-pivot bend contributes additional head displacement. It applies to both player and NPC in standing, walking and crouched custom ADS right lean. Neutral and left lean are unchanged.

Only the neck/head subtree is modified by this added pass, after weapon IK and the existing forward nod. Arms, hands, gun placement/cant, legs and the prior working animation controller stay unchanged. Scoped/suppressed unlimited-reserve Mosin, normal bolt cycle, damageable ragdoll target and 1-second respawn remain as in v19. Bodies and dropped target rifles are cleaned up as before.

F10 pauses the NPC for inspection; pause while he leans right to compare face exposure beside the rifle. Check your own right lean too; F8 enables third-person raised-Mosin inspection. F6 retains native ADS head-tilt comparison, correction enabled by default. F7 compares full native/custom lean; F9 records measurements.

Local checks verify the added right-only head-subtree path and unchanged range/pose logic. Native visibility, clipping and sight alignment need your in-game test. If wrong, send a screenshot and Collect-Logs.cmd ZIP (v20).
