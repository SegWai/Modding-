MovementLab lean test v88 — rifle shoulder height

Third-person player and NPC raised rifle/both arms lowered together by 5 cm toward shoulder height, including neutral and left/right leans. Upper-arm roots translate in model Y; muzzle direction and relative hand grip are preserved mathematically. The weapon attachment buffer is republished after the shift.
First-person crouch-style presentation from v87 is unchanged. Native stance/legs, head, lean distances, timing and camera code are unchanged. The new lowering follows the existing raised-pose gate; no extra delay.
Extract into a fresh folder under F:\DayZProjects and run Launch-Mosin-Lean-Test.cmd. Compare stock position against the right shoulder in third person/NPC, then check Q/E and grip while looking up/down. Confirm first person still matches v87. Collect-Logs.cmd collects diagnostics.
Local checks only; actual shoulder alignment, skin deformation and native playback need Windows DayZ testing. Previous packages remain rollback options.
