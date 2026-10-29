ALL APPROVED POSES COMPARISON - V213

All approved JSONs installed EXACTLY as bundled and active profile defaults,
including latest MLOneHandedWalkingLeanPreset. Separate named banks retained;
no lossy merge/rebase. Player approved standing/crouch/SMG/tool/onehandwalk routes
retained. Native third-person camera and pose graph unchanged.

30NPCs in3rows, same Denis model/scale, shared clock, nearby side-by-side slots:
GREY FRONT:19walking lowered previews (empty,AK74,SKS,SVD,MP5K,UMP45,Glock19,
Magnum,bat,sledge,axe,shovel,pitchfork,flashlight,compass,cola,crate,generator,barrel).
BLUE SECOND:8standing lowered previews (empty,AK74,Glock19,bat,sledge,flashlight,
crate,pitchfork), with STANDING preset banks, not their walking variants.
RED THIRD:3AK74examples, own-right order standingraised/walkingraised/crouchraised,
using existing original standingarmed/walkingarmed/croucharmed approved banks.

First12seconds reference setup, then all lean LEFT3s/RIGHT3s together. Walking
actors walk sideways IN PLACE; standing/crouched examples do not walk. All root
positions pinned for offline preview only. No ADS; raised means weapon-up pose.
Native IK can adapt grips per weapon. Unchanged heavy/pistol/bat/empty walking
uses existing standing bank on native gait, since no separate walks were authored.
SMG/approved tool group(no bat)/onehandwalking use their dedicated approved banks.

F6/F7 retain one-handed WALKING bank editor; affects matching walking actors
flashlight/compass/cola, NOT other categories or standing blue onehand actor.
Save both sides/F6/F7 to MLOneHandedWalkingLeanPreset.json. F6 item-offset rows
remain unsupported. This is a comparison test, not a new all-bank selector UI.
Walk your player back/around row to inspect. No camera-distance override.

Extract fresh, do NOT copy old Profiles over approved defaults. No other lean
workspace mod. Offline data/bank/movement/stance/scene/PBO checks pass; native
compile,30NPCperformance/visiblepose/grip/anchor/transitions still need testing.
