MovementLab lean test v101 — vertical-only left hold and expanded loadout

Removes v100 cross-body stock correction. Starts again from v95 lateral/depth hold, with only an extra 8.17cm model-Y downward hand/weapon target adjustment on the left, matching trigger-wrist height relative to RightShoulder from the approved right pose. Both hands translate equally in the authoring solve with wrist orientations/relative grip preserved. Uses existing joint rotations, no new IK overlay. Exact native stock contact remains unverified.
Right hold, first-person, stationary/crouched paths, head/torso/legs, camera and timing unchanged. Ctrl+F8 compares ON left height correction + approved right hold versus OFF v89 baseline. Automatic full pose/weapon captures per stable moving side/mode are retained.
PLAYER QUICKBAR:
1 AK74 with original attachments.
2 MP5K: stock, rail handguard, Reflex optic, universal light, batteries, pistol suppressor, 30-round magazine; auto mode selected.
3 FNX45: MRDS optic, TLR light, batteries, suppressor, 15-round magazine.
4 SVD sniper replacing Mosin: PSO1 optic, battery, AK suppressor, 10-round magazine.
Large Alice backpack and spare filled magazines added. Current held weapon ammo/suppressor refill supports all four. Any storage failure is logged and the weapon spawns on ground beside player. NPC keeps its AK74 for consistent arm testing. New MP5/FNX/SVD use native weapon handling; custom lean rig remains scoped to AK74/Mosin.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Let NPC walk both directions with Ctrl+F8 ON and OFF. Send video and Collect-Logs.cmd output if arm/stock remains wrong; MLSTOCK101/MLPOSE101 contain actual native matrices needed to resolve it.
Official 1.30 SDK debug-loadout class names and APIs checked. Native compilation, attachment compatibility, inventory placement and visual posing require Windows DayZ testing.
