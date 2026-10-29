SLEDGEHAMMER WALKING EDITOR - V209

ONLY ONE NPC: blue SledgeHammer, walking/leaning in place left/right after12s
reference setup. F6 arms/head and F7 body target ONLY this walking preview.
Independent MLSledgehammerWalkingLeanPreset.json starts exact approved bat
values, not SMG values. Save BOTH sides+F6/F7 to:
Profiles/LeanMosin/MLSledgehammerWalkingLeanPreset.json.
Send this to approve walking hammer pose; standing bat/other actors unaffected.
Axe/shovel/pitchfork walking group and flashlight are later steps, not spawned.

Uploaded MLSMGWalkingLeanPreset.json preserved EXACTLY as approved default.
Player lowered upright WALK speed1 with verified SMG families now uses it;
standing/raised/running SMG and rifles keep previous banks. Native SMG families
MP5K,UMP45,CZ61,PM73Rak,PP19,MP18 plus inherited modded subclasses. No universal
native SMG behavior type exists; unrelated modded SMGs need explicit integration.
Source caches reset on SMG walking-bank changes. Native IK can adapt arm contact.
All ten prior raw bank files unchanged except replacing the experimental SMG
walking seed with this approval. New sledge bank is experimental, not global.
Native camera and pose graph retained; F6 gun-offset rows remain unsupported.

Extract fresh and load no other lean workspace mod. Offline data/category/
scene/cache/PBO checks pass; native compile/gait/grip/editor/stability need test.
