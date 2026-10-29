LOWERED AK74 POSE EDITOR - V190

Red NPC position now contains a lowered AK74-holding editable NPC, not a vanilla
empty-handed comparison. Blue NPC keeps your approved unarmed pose unchanged.
Same positions/gap and SAME scene clock: left/forward/right/forward,1s each.
Opening F6/F7 holds BOTH NPCs on selected side so you can compare directly.
F6 arms/head and F7 body edits target ONLY the red armed NPC, including arm edits
previously suppressed for normal held items. Blue NPC and player approved banks
are not changed by this editor. Weapon remains lowered, ADS disabled in preview.
Native third-person camera height/distance/collision restored by removing the
inspection camera override. First-person/ADS camera code untouched.

Save in either editor writes BOTH sides and F6/F7 settings to ONE NEW file:
Profiles/LeanMosin/MLHeldLeanPreset.json. Send that file to approve the new pose.
It starts as an exact copy of the approved unarmed preset, but is independent.
Four approved JSONs remain byte-identical and retain their previous routing.
F6 weapon translation/rotation rows remain inherited unarmed-editor limitations;
use F7 body/arm/hand transforms to author this lowered pose. No new gun-offset
solver is claimed. Native held buffer publisher from v189 retained (0.0 fix).

Extract fresh; launch with Launch-Mosin-Lean-Test.cmd; no other lean mod loaded.
Scene/editor/independence/clock/preset/PBO checks offline only; native compile,
AK74 lowered grip, visible pose, camera and stability require an in-game test.
