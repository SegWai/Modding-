SODA CAN + BANDAGE COMPARISON - V214

ONLY TWO NPCs side by side .95m: GREY SodaCan_Cola and BLUE BandageDressing.
Same model/scale, same12sreference setup then synchronized3sleft/rightwalking
and leaning IN PLACE. No other previews. Both use their own native item IK.

F6 arms/head and F7 body edit ONLY grey soda-can NPC via NEW isolated bank,
initial exact copy of approved one-handed walking file. This reproduces current
pose as starting point; no unapproved fix to canonical pose. Bandage reference
stays on approved onehandwalking preset, not changed by soda edits.
Save BOTH sides+F6/F7 to Profiles/LeanMosin/MLSodaCanWalkingLeanPreset.json.
Send it to approve a separate soda holding exception later. It is NPC-only for
now; player soda still uses previous broad ONEHANDED route until approval.

All13approved/default JSON files, global player routing, native camera and pose
graph unchanged. Native IK can constrain arm edits; F6 item-offset rows still
unsupported. Extract fresh and launch with no other lean workspace mod.
Offline scene/bank/editor/clock/preset/PBO checks pass; native compile/grip/gait/
visible pose/editor response and stability need an in-game test.
