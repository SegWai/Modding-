PISTOL / BAT / SLEDGE CUSTOM LEAN - V193

Removed red SVD and green MP5K preview actors. Preview lineup:
blue empty-handed custom reference; grey Glock19; brown BaseballBat; black
SledgeHammer. Same model/scale, .5m gaps, stationary lowered (no aim/ADS).
ALL four share the same1sleft/forward/right/forward cycle and selected editor side.

New three item NPCs use your CUSTOM UNARMED torso/head/body lean, with native
item grip. They do NOT inherit the approved rifle/SMG arm offsets. Fresh new
preview bank starts with native arm offsets0, retaining custom torso/head/legs.
F6/F7 edits this separate bank on ALL THREE item NPCs; blue/player approved banks
stay unchanged. Native item IK can constrain arm edits to preserve grip.
Save writes both sides+F6/F7 to Profiles/LeanMosin/MLOtherHeldLeanPreset.json.
It is an experimental editing bank, not a replacement for any approved preset.
All FIVE approved JSON banks remain unchanged, including rifle held f4522bf7.
Player rifle-category default, crouch/walk/aim and native camera retained.
F6 weapon XYZ/PYR rows still not implemented as gun transforms; use F7body/arms.

Extract fresh, launch with no other lean workspace mod. Offline scene/isolation/
SDK categories/graph/preset/PBO checks do not establish native compile, item grip,
visible pose, transitions or stability. In-game retest required.
