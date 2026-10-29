# DayZ custom lean and fixed-left weapon handoff

Updated: 29 October 2026 (Europe/Lisbon).

## Current test v199: custom bat reference and independent sledge editor

User replaces grey vanilla sledge NPC with approved custom-JSON bat reference;
wants black sledge NPC editable to author a separate custom pose.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v199/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v199.zip` (26 files).
Grey BaseballBat uses original ML193 approved bat bank unchanged. Black
SledgeHammer uses new isolated ML199WeaponState/BodyState/Preset bank. Blue
unarmed reference unchanged. Same positions/model/scale/shared1sclock/selected
side hold. No vanilla NPC path remains in this scene.

F6 arms/head and F7 body menus+keys target199 only; shared clock follows199 side.
Native actual item grip/graph unchanged. Seed for new hammer bank EXACT byte-copy
of approved bat JSON d55bf37...; editing does not mutate bat reference, blue,
player global defaults or any of seven approved banks. Save both sides/F6/F7 to
`Profiles/LeanMosin/MLSledgehammerLeanPreset.json`. Send this to approve it later;
new bank is experimental until user approves. Player two-handed193 routing
remains approved bat default, not new hammer editing bank.

Added MLSledgePreset199.c and SledgeEditor helper/preview flags. No pose graph
change or extra IK. Source/scene/bank/menu/clock/7approvedJSON/seed/PBO26file checks
pass via tools/check_sledge_editor_v199.py. Native compile/render/grip/UI/perf
NOT RUN. Package tools/package_sledge_editor_v199.py. Camera native. Fresh folder.
F6 gun-offset rows remain unsupported; arms/head/body authoring available.

## Prior v198: broaden bat pose + native/custom sledgehammer comparison

User explicitly supersedes prior exact-bat restriction: apply bat JSON to
sledgehammers, axes, shovels and similar two-handed holding; remove bat NPC,
show native sledge lean against custom bat-JSON sledge lean.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v198/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v198.zip` (24files).
Native TWOHANDED behavior now selects approved bat bank, no DebugGetItemAnimInstance
or bat-name filter. Includes other native TWOHANDED items/containers; does not
force HEAVY/POLEARMS/PISTOLS/FIREARMS. Still lowered stationary standing route.
All seven approved JSONs exact; raised/crouch/walking banks unchanged.

Preview scene: grey SledgeHammer VANILLA native lean, black SledgeHammer CUSTOM
approved bat JSON, original blue empty-handed custom reference. No bat actor.
Shared181clock, model/scale, .5m spacing, selected-editor-side hold. Native factory
flag starts183nativeReference=true so helper disables custom stage and returns;
custom starts193editor bank. F6/F7 target BLACK only (and shared player bat bank
can reflect edits); native grey/blue unchanged. Save MLBatLeanPreset.json.
Native camera retained. Helper/graph/clock unchanged; new factory native flag and
native/custom actor cleanup. tests/check tool `tools/check_twohand_comparison_v198.py`
passes category/bypass/scene/allrawdata/isolation/source/PBO24file checks.
Package tools/package_twohand_preview_v198.py. Native compile/grip/visuals NOT RUN.

## Prior v197: approved bat default for matching bat holding profiles

User uploaded/approved MLBatLeanPreset.json, 14659 bytes, SHA256
`d55bf37cbc5a93729c7474a633e6c40a1c184fb17cecd63b27b631cc90dda98e`.
SEVENTH approved bank. Raw file preserved at kit root/bundle/active profile,
`Current-MLBatLeanPreset.json`, dated Approved archive, artifacts/MLBatLeanPreset.json.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v197/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v197.zip` (24files).

UsesBatHolding: native TWOHANDED guard AND animation-instance name contains
player_main_2h_bat; verified native Human.DebugGetItemAnimInstance declaration.
Fallback known native BaseballBat/NailedBaseballBat/BarbedBaseballBat/XmasBaseballBat
and subclasses if instance query isn't populated. Modded items sharing same ASI
match dynamically. Not all TWOHANDED tools: sledge/axes/shovels have distinct ASIs.
User informed exact bat family applies, unrelated two-hand tool poses not forced.
Native runtime query availability/string format remains untested (cloud Linux);
fallback covers native bat families. Do not claim arbitrary mod profile support
verified by declaration alone.

Player stationary lowered route sets helper OtherHeldEditor from matching bat
category, selects now-approved ML193/bat bank incl arm edits, caches invalidate
on bat-bank change. Six older approved banks untouched; pistol/rifle category,
raised/walking/crouch, graph/native camera, bat+blue scene and F6/F7 unchanged.
Offline tools/check_approved_bat_v197.py passes exact-data/native registrations/
API/exclusions/cache/scene/menus/graph checks; independent PBO24fileZIP passes.
Native compile, query behavior, actual hand fit/pose fidelity NOT RUN.
Package tools/package_bat_default_v197.py; fresh folder required.

## Prior v196: approved pistol default, bat editor preserved

User approved uploaded MLPistolLeanPreset.json, 14349 bytes, SHA256
`4ac93abf222dc4b51e23983a63e14820b9e81f59c42970e0adaae2cfd8a9bdcb`.
SIXTH approved bank. Exact raw root/bundle/active defaults plus canonical
`ads-lean-test/User-Presets/Current-MLPistolLeanPreset.json`, dated Approved copy,
and `artifacts/MLPistolLeanPreset.json`. No numerical/arm rebasing.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v196/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v196.zip` (24files).

Stationary upright LOWERED player holding uses approved pistol bank only when
native behavior ItemBehaviorType.PISTOLS, via verified accessor API. Independent
ML196WeaponState/BodyState/Preset; helper PistolBank uses its approved arm/body
settings, reference cache resets on item/rifle/pistol bank changes. This does not
replace raised aiming/crouch/walking. Matching modded objects supported without
classname lists. Handguns/revolvers/flare gun registered PISTOLS. Some SDK entries
such as DartGun/Shockpistol exist but do not infer currently playable vanilla loot.

User asked whether ordinary small items use item animation or empty-handed pose:
answer given: own holding/animation+IK profiles (toolsOneHanded category), not
empty handed. Examples Flashlight, Compass, SodaCan, Bandage all registered
item-specific one-handed tool profiles. Our mod uses custom unarmed BODY lean
with native item grip for those; never apply pistol pose based on object size.
No ordinary listed small tools found using PISTOLS. Flare gun is confirmed
special-purpose pistol-category item; modded registrations may add more.

V195 bat editor and blue reference/F6/F7/bat save remain unchanged. Approved
pistol bank independent of bat experimental bank. All5older approved JSONs,
graph, native camera preserved. Native compile/pose/grip NOT RUN. Offline
check_approved_pistol_v196.py passes exact data/category/SDK/source/scene/menu/
graph/reset/isolation checks; PBO24fileZIP passes. Package via
`tools/package_pistol_default_v196.py`. Fresh folder required.

## Prior v195: bat-only pose editor

User asks same editor for bat and remove pistol. Source
`ads-lean-test/MovementLab_ADS_Lean_Mosin_v195/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v195.zip` (22files).
BaseballBat NPC replaces Glock preview; blue unarmed reference stays unchanged.
Same positions/clock/editor hold. F6 arms/head and F7 body edit bat NPC only.
Combined save `Profiles/LeanMosin/MLBatLeanPreset.json`, both sides and F6/F7.
Seed unchanged from previous editor; no new pistol JSON was supplied/approved.
Five approved preset banks, graph, player/helper scripts, native camera and
clock remain unchanged. Scene/data/paths/PBO/runtime checks pass; native
compile/grip/editor/mesh/stability NOT RUN. Package tools/package_bat_preview_v195.py.
Previous pistol test/save preserved. Fresh folder. F6 gun-offset rows unsupported.

## Prior v194: pistol-only pose editor

User requested removing bat/sledge, keeping pistol and editing its pose.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v194/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v194.zip` (22 files).
Only grey Glock19 and blue unarmed reference remain, unchanged positions/clock.
F6 arms/head and F7 body continue targeting193 independent editor bank, now only
pistol actor remains using it. Titles identify LOWERED PISTOL. Combined save
renamed `Profiles/LeanMosin/MLPistolLeanPreset.json` (both sides/F6/F7), initial
values byte-identical prior OtherHeld bank. No approval of pistol preset yet.
Five approved banks, graph, player/helper scripts, clock/camera unchanged.
Offline 2-actor scene/editor hookup/data identity/PBO/runtime checks pass;
native compilation, grip, editor visuals/stability NOT RUN.
Package tools/package_item_previews_v194.py. Fresh folder; send saved pistol JSON
for later approval. F6 weapon-offset rows still unsupported; F7 body/arms works.

## Prior v193: pistol, bat and sledgehammer custom lean previews

User requests remove SVD/MP5 previews, add pistol/bat/sledge NPCs using custom
normal lean appropriate to their items. Source
`ads-lean-test/MovementLab_ADS_Lean_Mosin_v193/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v193.zip` (22files).
Lineup: original blue empty-handed reference; grey Glock19; brown BaseballBat;
black SledgeHammer, same Denis model/scale, .5m gaps. All four same shared1s
left/forward/right/forward clock, no raised/ADS. All removed actors gone from
mission factory/spawn; all four new/current actors clean up on exit.

New item previews use custom unarmed torso/head/leg pose with native item-grip
arm seed (zero relaxed-unarmed arm offsets), NOT rifle bank's approved arm values.
Separate experimental MLOtherHeldLeanPreset.json seeded from unarmed custom body,
cloned ML193WeaponState/BodyState/Preset, independent legacy/save paths. F6/F7
now edits ALL THREE item previews jointly; blue/player approved banks unchanged.
Combined save includes both sides+F6/F7 in new MLOtherHeldLeanPreset.json. New
bank not canonical/approved until user saves/approves. Rifle approved f4522bf7
and four older approved banks untouched. Player FIREARMS category routing from
192 unchanged. No authoring bank applied to nonrifle player by this scene change.

Helper OtherHeldEditor flag selects bank at Update (NOT Bind; caught generation
scope error before packaging), enables editor arm changes; native per-item grip
IK remains one-pass191. Locomotion graph byte-identical192, native camera stays.
Native compile/grip/visible poses/performance still NOT TESTED. Offline scene,
clock, preset isolation, bank scope, native bat/sledge TWOHANDED registrations,
PBO/22-file checks pass. tools/check_item_previews_v193.py;
package tools/package_item_previews_v193.py. F6 gun-offset rows still unsupported.

## Prior v192: approved held pose default + SVD/MP5K comparison

User approved new uploaded MLHeldLeanPreset.json, 14411 bytes, SHA256
`f4522bf7f9a4b153373f129c88d7353b7b316927ff409fde9a64e958cdd57ad4`.
This is now a FIFTH approved bank, alongside the four preserved banks below.
Raw bytes archived `ads-lean-test/User-Presets/MLHeldLeanPreset-Approved-20261029.json`,
canonical `Current-MLHeldLeanPreset.json`, artifact `artifacts/MLHeldLeanPreset.json`.
Kit root/bundled/active-profile copies EXACT. Do not zero its approved arm values.

Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v192/`; runtime
`artifacts/MovementLab_ADS_Lean_Mosin_v192.zip` (20 files).
Stationary lowered player held-bank selection now uses native holding behavior,
NOT physical gun length/classname allowlist: HumanItemAccessor
GetItemInHandsBehaviourCfg -> HumanItemBehaviorCfg.m_iType == FIREARMS.
SDK confirms AK74, MP5K and SVD share that behavior. Also covers modded objects
registered with the same FIREARMS holding category. Pistols, generic two-handed
tools/heavy objects retain other routes. Raised/walk/crouch banks unchanged.
New MLHeldCategory192.c; player sets helper HeldEditor from matching category.
Reference caches reset on item OR bank change to avoid stale item/empty poses.

Red NPC now SVD + PSO1/mag, lowered. New green MP5K + stock/handguard/mag at .5m
on red's other side; original blue unarmed reference stays in place. All three
same model/scale/181clock and selected-side editor hold; both armed NPCs same
ML190 bank. F6/F7 updates BOTH armed NPCs and eligible player poses, blue bank
independent. Native weapon IK may adapt hand contact per gun despite identical
saved body stats. Added SMG cleanup. Camera native; graph same as191.

Offline tools/check_approved_held_v192.py passes raw integrity (6copies), four old
banks, API/category/SDK registration, cache isolation, scene/clock/cleanup.
Independent PBO/20-file ZIP checks pass. Native compile/load/grip/perf NOT RUN.
Repackage via tools/package_held_preview_v192.py; fresh folder required.

## Prior v191: lowered-AK74 grip correction

User screenshot from v190 showed rifle near vertical and support hand floating.
V191 addresses two implementation mistakes: experimental held bank inherited
nonzero unarmed arm settings; final publisher used raised-grip configuration.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v191/`; runtime
`artifacts/MovementLab_ADS_Lean_Mosin_v191.zip`.

ONLY the new MLHeldLeanPreset arm/shoulder/hand offsets are zeroed; torso/head/
legs and all FOUR approved presets remain unchanged. Fresh folder required,
never copy v190 MLHeldLeanPreset into v191. Red arm edits still available.
Held branch is now native pre-IK pose -> custom body -> exact NormalWeaponIK
clone, once, retaining native RightArm rotator, ArmIK masks, aim/roll and native
output policy. Empty branch retains original pre-body NormalWeaponIK.
No forced limb weights. Native grip can constrain edits; actual rendering still
needs a test. Removed raised-profile/custom-output final publisher configuration.
One new binary pre-body selector, one base-child rewire, replacement publisher.
No gameplay scripts, NPC clock/scene, menus or camera changes. Native camera stays.

Offline tools/check_lowered_grip_v191.py checks exact native template, one grip
stage each path, experimental seed-only delta, four-bank/script/scene identity.
Independent PBO/20-file ZIP checks pass. Native compiler/game/grip NOT RUN.
Package via tools/package_held_preview_v191.py. Builder prefix Roll count now26,
explicit outputbuffertrue count20, reflecting cloned native output policy.

## Prior v190: synchronized lowered-AK74 editor NPC

User requests replacing the red vanilla empty-handed NPC with a lowered AK74
holder at the same location, synced to the existing custom blue unarmed NPC;
F6/F7 target the armed NPC only; restore normal third-person camera.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v190/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v190.zip`.

Red now uses ML190StartHeldComparison, no aiming/ADS, shared preview path.
Blue retains approved MLUnarmedLeanPreset and original body pose. Same two
actors/positions/.5m gap and shared 1s left/forward/right/forward clock.
Menus select held-bank side and BOTH NPCs hold that same side while editing.
Independent ML190WeaponState/BodyState/Preset cloned from183; seeded exact copy
of approved unarmed JSON but saves to NEW `Profiles/LeanMosin/MLHeldLeanPreset.json`
(both sides + F6/F7). Editors affect only red; original four approved presets and
player bank routing untouched. Helper chooses190 values only for HeldEditor;
held NPC publisher follows actual item; allows arms edits only on editor NPC.
F6 supports inherited arms/head and F7 full body. Inherited unarmed F6 weapon
XYZ/PYR rows are not a new gun-offset solver; see README limitation. Do not claim
those rows reposition the gun. No new feedback/recalibration loops introduced.
Removed MLInspectionCamera171.c; native third-person distance/height/collision,
first-person/ADS code unchanged. No shoulder swap. Graph byte-identical189 with
float0.0 startup fix retained. Native v190 compile/grip/UI/camera NOT tested.
Offline tools/check_held_preview_v190.py passes isolation/scene/clock/presets/
graph/floatfix/camera checks. Package via tools/package_held_preview_v190.py
(20 files, includes held bank root+active copy). Build PBOs with kit build_pbos.py.
Original189andearlierarchives preserved. Send user a fresh extracted runtime.

## Prior v189: fix confirmed v188 native graph-load error

Uploaded v188 logs (Mosin-Lean-v188-Logs-20261029-101012.zip) confirm World and
Mission compiled. Player creation failed because ML187_PublishHeldLean used
integer expression `0` for float WeaponDirLr, WeaponDirUd and WeaponRoll.
Native error explicitly says int but float expected; graph invalid then AV.
V189 changes ONLY these three expressions to `0.0`, preserving ALL gameplay
scripts, mission, routing, controls and four approved JSON banks byte-for-byte.
Source `ads-lean-test/MovementLab_ADS_Lean_Mosin_v189/`; runtime
`artifacts/MovementLab_ADS_Lean_Mosin_v189.zip`.
Regression `tools/check_graph_float_fix_v189.py` checks exact three-field delta
and scans weapon float expressions for invalid bare integer literals. Independent
PBO/18-file runtime checks pass. Native v189 graph reload/gameplay NOT RUN.
Do not attribute the v188 startup failure to JSONs, crouch pose or runtime lean
transitions: no pose calibration ran. Old offline checks missed this type error.

## Prior v188: all four approved banks with automatic crouch routing

User explicitly asked to include the approved crouch aiming JSON and ALL confirmed
presets in the new shared-standing test. Source:
`ads-lean-test/MovementLab_ADS_Lean_Mosin_v188/`; ZIP
`artifacts/MovementLab_ADS_Lean_Mosin_v188.zip`.
All four canonical raw JSONs are exact at root/bundled/active-profile locations.
V187 already bundled them, but did not automatically select the crouch bank.
V188 backports v186 stationary rifle-crouch routing plus isolated crouch reference
caches: three banks, six side references, twelve arm frames. Clears crouch hold
and refreshes writes on exit. Shared lowered standing held-item behavior from
v187 retained; standing raised/walking banks retained; no new crouch-walking or
pistol rifle-pose override. Graph, other scripts, NPC scene/camera unchanged.
12 preset hash checks, 64 scope cases, cache isolation and independent PBO/18-file
ZIP checks pass. Native compile/render/contact/stability still NOT RUN.

## Prior v187 implementation: shared normal standing lean with held items

After restoring v185, user asked that the current unarmed normal lean also apply
when holding an object or weapon. Implemented on restored-v185 base as
`ads-lean-test/MovementLab_ADS_Lean_Mosin_v187/`, runtime
`artifacts/MovementLab_ADS_Lean_Mosin_v187.zip`.

Scope stated to user: stationary upright LOWERED holding; raised/ADS/walk/crouch
retain previous behavior. Real player and non-preview actors use the approved
unarmed torso/head/body pose irrespective of held class. Native grip arms are
retained: no unarmed arm offsets on held items. Two-node gated native RIGHT-hand
publisher republishes held buffer after body changes, with aim/chain weights off.
This generic item attachment integration remains UNTESTED in DayZ. Do not claim
visible grip fixed. Empty/native NPC graph branch unchanged. Reference snapshots
clear on held-item entity change. Release clears stages and invalidates caches.
No player Lean/Raised/ADS forcing. 512 scope cases, exact graph delta/isolation,
presets/mission identity and independent PBO/18-file runtime checks pass.
See tools/check_shared_standing_v187.py and latest ads-lean-test/AGENTS.md entry.
Four JSONs, old archives and the v185 NPC scene remain unchanged.

## Previous restoration request: v185

The user subsequently requested v185 again with the JSON sent after v185 as the
default standing pose. Delivered source:
`ads-lean-test/MovementLab_ADS_Lean_Mosin_v185_Restored/`.
Runtime: `artifacts/MovementLab_ADS_Lean_Mosin_v185_Restored.zip`.

The later JSON is approved `MLUnarmedLeanPreset.json`, SHA256 d47025fd... (full
hash below). It is copied exactly to bundled, active-profile and root defaults.
All four canonical presets are included. Original v185 scripts, graph, camera,
controls and two-NPC comparison scene remain byte-identical. This intentionally
does NOT include v186 player rollout or any left-hand/shoulder experiment.
Original v185/v186 and v10 archives remain preserved. Source/data identity and
packaging checks pass; native DayZ test not run. The rest of this document
records the previous v10 work for continuity, not the current requested baseline.

## Previous v10 goal and history

The user wants real, visible left-handed weapon holding: **left hand on the
AK74 pistol grip/trigger, right hand supporting under the fore-end**, with the
**camera permanently on the left**. There is no shoulder-swap button anymore.
They also want the stationary stance reversed: **left foot behind right foot,
right shoulder forward instead of left shoulder forward**, both standing with
the gun lowered and standing aiming/raised, including ADS.

**Current implementation is experimental. No native DayZ run has been performed
in this Linux workspace. Do not describe the gun placement or grip as fixed.**
The user has repeatedly tested earlier builds and reported badly rotated or
misplaced weapons. Pure transform tests did not establish native behavior.

The latest request, after finishing the test, was to create this detailed
`handoff.md` for another Codex chat. The file is in the repository root.

## Repository, environment and delivery

- Repository: https://github.com/SegWai/Modding-
- Cloud path: `/workspace/Modding-`; branch `work`; publish via
  `git push origin HEAD:main` (previously authorized by the user).
- Current test source: `shoulder-swap-test/MovementLab_LeftHand_Lean_v10/`.
- Current runtime: `artifacts/MovementLab_LeftHand_Lean_v10.zip`.
- This handoff is committed with the v10 test; get its exact commit using Git.
- Prior fixed-left v9 commit: `0c7175c`.
- Prior shoulder v8 commit: `b4e00e7`.
- Prior shoulder v7 commit: `ddfd497`.
- Deliver immutable raw-GitHub ZIP links pinned to the published commit, e.g.
  `https://raw.githubusercontent.com/SegWai/Modding-/<commit>/artifacts/MovementLab_LeftHand_Lean_v10.zip`.
- Runtime ZIP contains 18 essential files. Source/authoring files stay in Git.
- Extract into a fresh folder; run `Launch-Mosin-Lean-Test.cmd`.
- Original lean and experimental fork override the same native workspace and
  modded player classes: **do not load both mods simultaneously**.
- Windows DayZ, its native Enforce compiler, DayZ Tools and desktop/game control
  are not available here. Do not suggest that cloud coding grants desktop access.
- User has VS Code/Codex installed locally and previously downloaded the project.
  Actual local installation paths and tool access should be checked there.
- Leave unrelated `tools/__pycache__/` untracked.
- Read `shoulder-swap-test/AGENTS.md` for fork-specific instructions/history.
  Later entries supersede earlier implementation details. Original-mod history
  is in `ads-lean-test/AGENTS.md`.

## Original lean mod: preserve it

The original approved lean project is a separate immutable baseline:

- Commit `3aff8a4`; pushed tag `lean-mod-saved-v186`.
- `ads-lean-test/MovementLab_ADS_Lean_Mosin_v186/`.
- `artifacts/MovementLab_ADS_Lean_Mosin_v186.zip`.
- Do not replace it or mutate its runtime ZIP while developing this experiment.

The work started with custom standing/walking armed lean animations and grew
into crouched and unarmed banks, live editors, native aim tracking and crash
fixes. The user wants matching player/NPC poses, stable support contact,
consistent first/third-person poses and smooth lean transitions. Earlier NPC
comparison scenes were removed; the current fork spawns **no NPCs**.

Four approved schema-1 absolute preset banks remain byte-identical in v10:

| File | Purpose | SHA256 |
| --- | --- | --- |
| MLLeanPreset.json | Standing raised lean | aefdc1486d065d12c743e30e3a9d40fbfc6b0b1139e4beaaea3464d49ddda53d |
| MLWalkingLeanPreset.json | Raised walking lean | 8828945ff4dc5eb7e0b2d8de7adddfff463ec5403db61de44b56b10a16ce42c2 |
| MLCrouchLeanPreset.json | Crouched raised lean | 2de68073870eb3b17bf24f9546ff90a41b737b516b0535351eae6d247f90eb20 |
| MLUnarmedLeanPreset.json | Standing unarmed lean | d47025fd4275847815d0fda2d34b629d057608355e7fb5d47e79f4b71d859a27 |

Canonical copies: `ads-lean-test/User-Presets/Current-<filename>`.
Each kit also has root, `LogicSource/Presets/`, and active
`Profiles/LeanMosin/` copies. Old extracted active profiles can override defaults.
Never zero-rebase, casually mirror, or replace these user-approved JSON files.
The new stance is a procedural layer, not an edit to these banks.

## Decisions and present behavior

1. The original lean mod remains saved separately.
2. Fork uses native default third-person camera height/distance; its old
   `MLInspectionCamera171.c` override was removed in the initial fork.
3. Original shoulder-swap mB4 action was explicitly removed in v9. No swap
   action/input registration remains. Camera is fixed left in normal movement.
4. Native held-weapon entity, inventory and firing state machine are retained.
   No weapon clones, detach/delete/recreate, item teleporting or fake visual gun.
5. Left-handed poses use a neutral-basis reflection of the actual source pose.
   Do NOT reflect absolute bone rotations with naive `S*R*S`: that previously
   inverted a torso/head. Reflect deformation from the destination neutral basis.
6. Source snapshots are captured only while correction outputs are zero, then
   cached. Never repeatedly recapture corrected output or rebase sliders from
   their own procedural result; earlier attempts caused rotating arms/crashes.
7. Camera left does not prove gun left: in v9/v10 fixed-left camera is deliberate,
   independent of whether a usable left weapon pose has calibrated.
8. V10 retains native behavior for reload/weapon-manager actions, unsupported
   contexts, and moving with weapon lowered. It is not a complete authored
   ambidextrous action set. Transitions can briefly show native right-handed pose.

## Current v10 changes and files

All paths below are relative to `shoulder-swap-test/MovementLab_LeftHand_Lean_v10/`.

### `LogicSource/Scripts/4_World/MLAShoulderPose.c`

- Mirrored hierarchy expanded from 50 upper bones to **62 bones**:
  pelvis, four spine bones, neck/head, both complete arm/roll/hand/finger trees,
  both thigh/shin/foot/toe chains. Parent-first order is essential.
- Six coefficients per bone: Rotate XYZ, then Translate XYZ, in model space:
  **372 mirrored pose coefficients**, plus 6 helper-anchor coefficients and
  one activation control = **379 MLASwap controls**.
- Centred stationary upright stance uses pelvis as mirror root and reflects
  the spine and opposite anatomical leg poses. This exchanges foot fore/aft
  placement and shoulder lead. Applies lowered, raised and ADS.
- Crouch, walking and non-centred lean preserve their previous torso/leg pose;
  upper limbs retain left-trigger/right-support roles. Avoid reversing custom
  Q/E lean direction by mirroring the entire leaning body.
- Lowered stationary centred holding was added with **separate cache keys**:
  72 slots total; old 36 stance/gait/lean/ADS keys plus 36 for lowered contexts.
  Only stationary upright centred lowered contexts are enabled.
- Reload/weapon-manager `IsRunning()` excludes the handedness layer.
- Native right-handed source support wrist is the original **LeftHand**.
  Its position is converted to source gun/sight-local coordinates and transported
  through the same target gun transform used by the publisher.
- `FitSupport(...)` performs one cached finite two-bone right-arm solve to that
  target, preserving upper/lower lengths, elbow pole, wrist/finger orientation.
  It updates desired upper/forearm roll frames and translates hand/fingers.
  Unreachable/degenerate targets keep the mirrored pose and log false; no stretch.
- Desired frames are finalized before the parent-relative coefficient pass.
  This prevents support corrections being encoded against stale parents.
- Left trigger hand/finger posture remains the mirrored original right grip.
- Camera `Override3rdIsRightShoulder(ENABLED, false)` stays left. Existing death,
  unconscious/no-move-command lifecycle releases override.
- Build/contact messages use `[MLLEFT10]`; inherited generic state messages can
  still say `[MLASHOULDER]`. Logs include standing mirror/contact solve success.

### Weapon attachment inherited from v8/v9

- The native animation skeleton has helper bone `Weapon`, parent `Pelvis`.
- Six helper-only proc nodes after shared late aim drive a virtual anchor at the
  left grip. Left WeaponIK publisher uses `hand=Weapon`, `weaponrotator=Weapon`,
  native right profile offsets, `weaponaxis=-x`, both chain weights false.
- Full rigid profile inversion uses the original accessor sight frame and right
  trigger-hand transform, reflects desired sight position/orientation, then
  solves the anchor rotation AND translation relative to the mirrored left wrist.
- Runtime helper baseline reconstructed from unmodified pelvis and cached native
  helper local frame; current left wrist supplies tracking. It does NOT read the
  corrected helper for its own baseline. Last evaluated frames can imply lag.
- **This helper/publisher approach is not natively validated.** Accessor sight
  frames may differ from the actual rendered attachment. Native WeaponIK may
  interpret helper/offsets differently. Do not assume more algebra proves it.

### Other modified authoring/runtime files

- `WorkspaceSource/locomotion.agf`: regenerate 372 parent-first mirror proc nodes;
  final before-aim selector points to `MLASwapPose371` (formerly299).
- `WorkspaceSource/player_main.agr`: 72 extra float controls, fresh control GUID,
  private `MLADSLeanLocomotion_LeftHand-v10.agf` resource and fresh resource GUID.
- `LogicSource/config.cpp`: version label v10; no shoulder input registration.
- `build_pbos.py`: private resource naming/revision v10; rebuilds and independently
  parses/hashes the two PBOs, compares payloads with source.
- `Launch-Test.ps1`, `Collect-Logs.ps1`: v10 labels/log archive names.
- `README.txt`: scope, installation, experimental limitations.
- Rebuilt `@MLAmbidextrousLogic/Addons/MLAmbidextrousLogic.pbo` and
  `@MLAmbidextrousWorkspace/Addons/MLAmbidextrousWorkspace.pbo`.
- Generated validation/provenance files reflect the new build.
- `Missions/MLADSLeanMosin.ChernarusPlus/init.c` unchanged: no NPCs, automatic
  initial neutral skeleton setup, native AK74/SKS/Glock and backpack loadout.
- Root additions: `tools/check_fixed_left_stance_v10.py`, this `handoff.md`,
  updated `shoulder-swap-test/AGENTS.md`, legacy text handoff appendix, runtime ZIP.

## Controls

- Q/E: lean left/right through existing native/custom routing.
- Native raise/ADS, WASD and camera look: normal game bindings.
- F6/F7: inherited weapon/head/arm and body editors; original bank/context routing
  remains. They are **not** a newly implemented editor for all v10 mirror/anchor
  coefficients. Recent original editor scene was for unarmed-bank editing.
- Ctrl+F1: inherited native/custom comparator; disabling custom mode disables
  left pose while fixed-left camera remains left in this fork.
- Ctrl+F8: inherited arm comparison.
- X: inherited freeze control (historical freeze/lean crashes exist in old builds).
- Alt: native freelook; do not repurpose Alt as freeze again.
- No custom mB4 action. An old user profile may still contain an obsolete binding,
  but this mod no longer registers or handles it.
- `Collect-Logs.cmd` / `.ps1`: collect logs after test.

## Evidence and previous failed approaches

- v1 (`d767d0a`): native compilation failed because field `Weapon` collided with
  native type name. v2 renamed to `HeldWeapon` (`eda1e06`), compiled natively.
- v2 native crash during graph/player creation, before pose activation. v3
  (`523d485`) replaced novel `max()` gate expression with known `clamp()`;
  subsequent gameplay worked. Root cause not symbol-proven.
- v4 (`2c19a8a`): automatic neutral setup; camera follows actual active pose
  instead of request-only. Video confirmed gun shifted left but badly placed.
- v5 (`1921c19`): corrected native weapon axis and disabled original unmirrored
  secondary arm solve; still poor placement.
- v6 (`ec919a6`): bounded roll probe/support calibration failed. Native logs show
  source/left accessor forward dot .686012 (~46.7 degrees), up dot .99213,
  5-degree roll probe response -.000937468 degrees, support target unreachable.
  This is not evidence for a hardcoded +/-90 roll fix.
- v7 (`ddfd497`): virtual Weapon-helper frame conversion. User still reported
  wrong placement; no v7 native logs proving helper semantics available.
- v8 (`b4e00e7`): corrected missing full hand-to-sight translation and mirrored
  gun direction. Offline math passed; no supplied native v8 success evidence.
- v9 (`0c7175c`): fixed-left camera and automatic raised pose, removed swap action.
- v10: requested stance reversal and explicit gun-relative right support target;
  current test awaiting native feedback, not a confirmed functional baseline.

Latest relevant supplied media/logs (local workspace attachments may be absent
in another chat/environment):

- Video `DayZ 2026-10-28 23-13-03.mp4`, sediment file
  `file_0000000055d881f4a7ca93db6a007706`; shows misplaced/canted gun and hands.
- V6 logs `Mosin-Lean-Shoulder-v6-Logs-20261028-232815.zip`, sediment file
  `file_000000007f9481f4940abd282b2ef3fc`.
- Reviewed video frame `/tmp/shoulder6-video/left.png` and contact sheet.
- Extracted logs `/tmp/shoulder-v6-logs`.
- No native v9/v10 logs yet. Never present old videos as v10 validation.

## Checks completed for v10

- `python tools/check_fixed_left_stance_v10.py` passes:
  62-bone hierarchy/opposite-map involution, 372 control-to-bone mappings,
  379 unique swap controls, graph dependency cycle check;
  foot fore/aft and shoulder-lead reversal examples;
  3000 finite two-bone/contact transport cases, max length error ~8.88e-16;
  separate lowered cache/action exclusions; fixed-left camera/input removal;
  four approved presets byte-identical to v9.
- `python shoulder-swap-test/MovementLab_LeftHand_Lean_v10/build_pbos.py` passes:
  independent PBO parser validates prefixes, source payloads and SHA1 trailer;
  inherited resource/graph checks pass. This is not native compilation.
- Runtime packager independently reopens/checks all 18 ZIP payloads.
- Native Enforce compile, graph load, gun attachment, left/right grip, firing,
  ADS, FPS, clothing deformation and transition behavior **NOT RUN**.

## Next steps for local Codex / native test

1. Confirm the fresh v10 launcher actually loads only the two fork PBOs and the
   correct profile folder. Inspect launcher-run.txt and `[MLLEFT10]` log marker.
2. Compile/load in Windows DayZ; fix the FIRST native error narrowly if any.
   Do not use cascade errors as independent root causes.
3. Test AK74 stationary lowered, raised, ADS, then Q/E and walking, reload and
   gun change. Confirm camera stays left and action exit restores native safely.
4. Compare side/front/rear views: left pistol grip, right fore-end, right shoulder
   ahead, left foot behind. Record whether `support_contact_solved` is true.
5. If contact still fails, first determine whether the Weapon-helper publisher
   changes the **rendered item attachment**, rather than endlessly adjusting
   mirrored arms/offsets against an accessor camera frame. Diagnose actual native
   profile/attachment semantics. A proper left-hand IK/action asset may be needed.
6. If source skeleton/helper baseline varies during locomotion, cached profiles
   can drift. Last-frame wrist tracking may lag. Test this explicitly.
7. Check crouch/lean gait and FPS; current stance mirroring is intentionally only
   upright centred stationary to avoid mirroring Q/E direction or walking gait.
8. Preserve original186 and the four JSONs. New user-approved JSONs must be saved
   exactly with an archived prior copy, never assumed equivalent to old data.
9. Build, package, commit and push only concrete reviewable changes. Deliver a
   short pinned download link with honest validation limits.

## Communication and coding cautions

The user is very frustrated by long waits and repeated ineffective tests. Act
on authorized requests, give meaningful progress updates within ~60 seconds,
and do not ask repetitive confirmations. Do not claim a native fix from offline
math. No subagents unless user/instructions explicitly request delegation.

Enforce/native pitfalls: `Weapon`/`Bone` field-name collisions; reserved `local`;
indexed array++ unsupported; complex arithmetic can yield FormulaTooComplex or
BrokenExpression; use intermediate values. Bone missing is -1 (other negative
IDs may be valid). Native bone matrices expose basis columns; ML144Rot stores
rows. Proc model rotations use negative-RH XYZ via AppendNative. AnimSetFloat
belongs in post-super CommandHandler; UI caches changes only. Avoid novel graph
expression functions and avoid fractional replay of huge base graphs (old native
operation-count overflow/crash). No verified generic held-weapon matrix setter
or native full left-handed inventory/FSM switch is available; do not invent one.

Temporary generation scripts `/tmp/build_left10.py` and older builders are not
canonical: post-generation changes exist and copytree fails if destination exists.
The committed source is authoritative. Rebuild using the kit's build_pbos.py.
