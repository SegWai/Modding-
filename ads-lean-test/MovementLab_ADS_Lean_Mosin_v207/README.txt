SMG WALKING EDITOR FIRST - V207

Lineup ONLY MP5K,SledgeHammer,WoodAxe,Shovel,Pitchfork,Flashlight (.85m gaps).
Bat,empty reference,rifles,pistol,crate and other previews removed from scene.
Blue MP5K is EDITABLE. Other five are comparisons, not affected by SMG edits.
Same12sreference setup then synchronized3sleft/3sright walking-in-place/leaning.
Opening editor holds selected side AFTER warmup; NPCs continue walking.

F6 arms/head and F7 body target ONLY the MP5K walking preview. NEW independent
MLSMGWalkingLeanPreset.json starts exact previous held-rifle/SMG values; edits
DO NOT alter standing SMG/rifle banks, other actors, bat pose or player routes.
Save BOTH sides+F6/F7 to Profiles/LeanMosin/MLSMGWalkingLeanPreset.json.
Send it to approve/apply walking SMG changes later. This is a preview editor,
not an automatic global SMG walking rollout or new authored locomotion clip.

Sledge/axe/shovel/pitchfork walking tuning is queued separately from BAT, which
looks good. Flashlight walking will also get separate tuning after SMG. Their
current previews retain existing approved banks; no unapproved changes made.
Ten approved/default raw bank files and pose graph unchanged. Native camera.
F6 gun-offset rows still unsupported; use body/arm/head controls. Native IK may
constrain arm edits. Extract fresh; do not load other lean workspace mods.
Offline actor-scope/bank/save/clock/preset/PBO checks pass; native compile,
walking grip/edit response/foot motion/root pin/performance need an in-game test.
