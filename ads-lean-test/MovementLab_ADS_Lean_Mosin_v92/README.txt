MovementLab lean test v92 — right-lean arms 7cm lower

Based directly on the user-selected stable v89. Adds 7cm model-Y lowering to both arm subtrees at full anatomical RIGHT lean (positive native lean), smoothly proportional to lean amount. Hands, elbows and attached rifle follow together. Left lean and neutral retain v89 values. Shared third-person player/NPC path; first-person crouch-style view is unchanged.
Existing v89 configured 20cm lowering is preserved: full-right configured total is now 27cm. No v90/v91 arm-target solver or movement-height changes are included.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Check NPC own-right lean, then own-left and neutral for comparison. Collect-Logs.cmd collects diagnostics.
Local source/graph/package checks only; exact visible displacement needs Windows DayZ testing. V89 remains the rollback.
