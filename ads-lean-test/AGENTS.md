# Lean-test package preferences

- Launch lean-test batches directly. Do not add numbered native/custom menus or `choice` prompts. Latest user request makes custom aiming leans permanent: do not restore F7/F8 native/off comparisons; keep the exact v79 rollback separately. Explain remaining in-game keys.
- The user's menu request applied only to the separate FPS graphics-settings helper. Preserve its apply/restore menu.
- Use `F:\DayZProjects` as the default project root in new packages. Treat the Steam game-install directory as a separate path.

- Apply pose and animation corrections through the shared player/NPC graph so identical stance, gait and lean inputs receive identical corrections; do not add NPC-only pose changes.
- Keep the approved custom raised-weapon pose in both first and third person, including aiming without ADS. The user rolled back v73/v74: v71 is the approved baseline. Latest request speeds up transitions: follow native interpolated lean without extra lag; short 0.08s custom raise/gait envelopes. Preserve approved poses/grip timing and isolate camera changes. Preserve the user-approved v79 native-head-bound first-person camera and native game animation timing; do not restore default first-person poses or restrict custom raised posing to third person.
- Future mod test ZIPs must contain only runtime/diagnostic essentials (PBOs, mission, launcher, log collector, required manifests and short instructions). Do not include Blender files, templates, clips, previews, importers or Blender build helpers. Keep authoring data and source in the repository rather than the runtime ZIP.
- For lean-distance balancing, use measured original DayZ distances from the same standing/weapon/aiming state as the target, rather than inventing a centimetre value. Keep the custom silhouettes similar and feet planted. Report any meaningful vanilla left/right asymmetry before choosing a shared symmetric target.
- Latest target: standing raised/aimed head travel from neutral is 42 cm character-left and 21.9 cm character-right. This supersedes the symmetric 32 cm root-centre target. Preserve earlier approved pose style, planted feet, walking/crouching and first-person behaviour.

- V79 camera fix was confirmed by the user. V80 bypasses stock raised-lean chains for Mosin/AK74; lowered lean and other weapon behavior stay native. Keep v79 ZIP unchanged as rollback.

- User rolled back v84: v83 is the baseline. Do not restore v84 selective smoothing. Current request targets the left raised-view dip while keeping the working right transition and final poses.

- Latest first-person request: use raised crouch lean upper-body rotation chains for both directions while raised in first person, preserving actual stance/legs and third-person/NPC poses. This view-specific presentation is explicitly requested; do not force native crouch or add NPC-only posing.

- User selected v89 as the stable baseline, discarding v90/v91. V92 starts from v89 and adds 7cm downward to both arms during anatomical right lean only, shared third-person player/NPC path, leaving first person unchanged.

- User rolled back left-side edits v95-v98 to v94. V99 starts from v94 and changes only the left elbow bend direction by 25 degrees, preserving the approved right lowering and Ctrl+F8 comparison. Do not restore v95-v98 gun shifts or elbow overlays.

- Latest user request restores the exact v95 matched left/right lowering and Ctrl+F8 comparison. Discard v96-v99 elbow-angle experiments for subsequent work; v95 is the current requested setup.

- Current user returned to v95 matched lowering, then requested left stock contact to match approved right shoulder contact. V100 starts from v95; v96-v99 elbow experiments remain excluded. Preserve approved right hold and Ctrl+F8 comparison.

- Current user returned to v95 matched lowering, then requested left stock contact to match approved right shoulder contact. V100 starts from v95; v96-v99 elbow experiments remain excluded. Preserve approved right hold and Ctrl+F8 comparison.

- V100 produced a backward-folded right arm. V101 discards its lateral/depth correction, starts from v95 with a vertical-only left hold adjustment, keeps right hold/Ctrl+F8/native pose captures, and adds player MP5K/FNX45/SVD loadout (replaces Mosin; NPC remains AK74). New guns retain native handling; ammo refill includes them.

- Latest request: during left-moving lean, left elbow down/in near torso and right elbow out; explicitly equip player backpack. V102 tests one-shot native-pose elbow calibration with private wrist target names, bounded before/after captures and Ctrl+F8 comparison. V101 weapon loadout retained; native outcome pending.

- Latest user request: left support elbow points down near torso (155 degrees interpreted as 25 degrees from vertical down), right elbow remains out. V104 uses fixed-wrist axis swivel with wrist counter-rotation and removes the left IK2 re-solve. Replace prior player weapons with The Panacea Weapons (Workshop 2389010221); exact classes from uploaded types.xml: PNC_W_SCARH, PNC_W_HoneyBadger, PNC_W_AWM, PNC_W_Origin_12ga. Keep backpack and NPC AK74 pose reference. Do not redistribute Workshop files. Native outcome pending.

- Latest scope: custom lean must work across firearm categories and modded subclasses, not only AK74/Mosin. V106 centralises actual Weapon_Base classification: all shouldered firearms share custom body/arm profile; native handgun/revolver ancestry uses custom body with rifle-only arm/IK corrections masked. Existing mod native weapon/FSM profiles remain required; Panacea fists/switching fault is not yet isolated. Do not claim every gun visually validated or firing fixed without native evidence.

- V106 did not fix Panacea handling. A separate Panacea_Weapon_Handling_Check_v1 diagnostic session loads only Panacea plus a minimal DayZDiag inventory PluginManager compatibility helper. No custom workspace/PlayerBase/camera/ammo loop/profile overrides. Quickbar 1 AK74 control, 2 SCAR-H, 3 AWM. This is a temporary fault-isolation test, not a rollback or a change to the custom pose requirements. Native results pending.

- Native Panacea handling check logs 2026-10-27 02:02 UTC confirm no custom workspace loaded: AK74 raises normally, SCAR-H falls back to generic Rifle_Base.InitStateMachine and fails WeaponStableState.ValidateMuzzleArray at spawn; AWM is generic BoltActionRifle_Base and throws null at Weapon_Base.ProcessWeaponEvent while firing. Installed mod mounts one PanaceaWeapons.pbo from Workshop 2389010221. Custom Panacea script registration/content loading is suspect, not proven missing until PBO script-path inspection. Panacea_Script_Inspection_v1 is a read-only header/config-metadata helper, no game launch, no animation changes; native PowerShell execution untested locally.

- User abandoned Panacea and selected AJs Weapons, Workshop 3571685323. V107 retains v106 animation workspace/camera/category scripts byte-for-byte, switches launcher to AJ only, and selects up to four distinct public non-DZ-model AJ firearms from installed config (preferred handling variety, fallback available). Loadout rejects generic script fallback classes, requires native running FSM and successful ammo loading, uses compatible installed attachment definitions. Keep backpack, NPC AK74 and Ctrl+F8. No Panacea launch/loadout. Native AJ compilation/handling/visual validation pending.

- User confirmed v107 AJ weapons all work. Latest elbow target supersedes 25 degrees: left support elbow 45 degrees away from straight down toward torso during own-left walking raised lean. V108 changes only native left pole direction coefficients to (+/-0.70710678, -0.70710678, 0); right elbow, fixed-wrist math, AJ loadout, camera and workspace retained. Native elbow appearance pending; fixed wrist reach constrains actual angle.

- User corrected direction: left elbow 45 degrees away from vertical down, AWAY from torso, not toward it. V109 reverses only left pole horizontal component (outward from left shoulder relative to torso); keeps downward component, right elbow, AJ loadout, camera and workspace. This supersedes the inward v108 target. Native appearance pending.

- AJs_Weapons_Scripts explicitly requires JM_CF_Scripts. V110 is a launcher-only fix: detect Community Framework (CF), Workshop 1559212036 / @CF, require an installed Addons directory and load CF before AJ (3571685323), workspace and logic. Gameplay PBOs/mission/elbows byte-identical to v109. Do not omit CF in future AJ launchers. Native launch pending.

- Latest elbow targets for the same own-left raised walking lean: RIGHT 45 degrees from straight down, outward away from torso; LEFT 20 degrees from straight down, outward away from torso. V111 changes pole directions only and removes the right forward-pole fallback that would override the requested direction. Shared NPC/player scope; keep AJ loadout, CF dependency and Ctrl+F8. Native achieved angle is reach-constrained and unverified.

- Latest user request: weapon during own-left walking lean +5cm toward CHARACTER RIGHT. V112 re-solves existing 18 ML32 arm/forearm/hand rotations from current captured left reference with common wrist shift [+0.05,0,0] model metres; preserves wrist orientation/limb lengths in reference. Retain left20/right45 outward elbow targets, right-moving hold, first-person/crouched paths, AJ/CF and Ctrl+F8 scope. Native gun displacement/contact pending.

- V113 user asks weapon 3cm left NOW: interpreted relative to v112 +5cm-right hold, giving net +2cm character-right from original left hold. Both wrists re-solved to [+0.02,0,0] model metres relative v101 reference; exactly -0.03m X vs v112. Other scopes/targets retained; native visual check pending.

- Latest combined v114 scope: replace sideways left-walking hold offset with +5cm character-forward (+model Z), net model X zero from original reference. Remove all added notifications and old test controls except Ctrl+F8. Add female SurvivorF_Eva 10m to ORIGINAL MALE NPC OWN RIGHT (user explicitly clarified). L tap records/stops, colon loops, L during playback stops without recording, hold L 0.75s clears and resets. New replay uses native locomotion and sampled movement/stance/lean/raise/aim, starting weapon/direct attachments; no action/firing/reload/inventory/jump replay. Max 6000 samples (~5min), session memory only; corpse/one-second respawn maintained. Shared pose graph; only female receives replay overrides; original male patrol retained. Native compilation/replay not run here.

- V114 native logs failed World compilation at MLMimic114.c:49: local is an Enforce reserved keyword. V115 renames only that parameter/references to localOffset; no replay/pose/mission behavior change. Do not use local as any script identifier. Native recompile pending.

- V116 user clarifies 5cm FORWARD ALONG THE WEAPON BARREL, so stock exits shoulder. Replace v114 character-Z offset, do not stack another 5cm. Restore pre-offset v111 ML32 coefficients, read live same-pose sight forward and both wrist axes, project one 0.05m vector into each wrist local space; private graph shift/capture/undo/native IK2/publish layer after old elbow/grip path. Seven new nonalias controls, read orientation only (no positional feedback). Enables after existing elbow calibration; same own-left walking third-person shouldered-gun scope and Ctrl+F8. Recorder/localOffset compile fix, controls and camera retained. Native displacement/IK/stock clearance untested.

- User frustrated by complex v116 approach; v117 discards v116 and earlier pre-solve forward offset, using one 5cm model-forward translation at each Shoulder root after existing elbow/grip solve, then republishes weapon offset. No new native controls/calibrator. Whole arm chains/hands should move together; native propagation unverified. Retain v115 recorder compile fix and other features.

- V117 native logs supplied: native RightShoulder/LeftShoulder local offsets under Spine3 are identical across L/R; v117 translation is not observed in those transforms. Stable male wrist-from-shoulder means: left [.136219,.026179,.033844] (228 samples), right [.118506,-.006794,.110190] (229). Full poses 34317_true (left after elbow) and 37464_true (right lean .98) are now the native reference. V118 replaces failed translation with 18 late model-axis native arm/forearm/hand rotations, shoulders fixed; calibrated right shoulder/weapon point transfers contact to left with common hand shift [-.034484,+.008141,+.094701]m. Real native hierarchy/matrices used, no older authoring reference. Grip orientation and lengths preserved in math. Wait for old elbow calibration before applying to avoid sampling shifted baseline. Stock proxy is bone-based, not a measured mesh vertex; .98 right full-pose sample plus stable traces used; actual rendering/contact pending. Recorder/camera/controls unchanged.

- V119 manual coordinate request: relative to native v117 reference retain X=-0.034483846m and Y=+0.008140797m, set Z=+0.15m (not another +15cm). This adds +0.055298662m Z from v118. Only 18 contact-layer rotation amounts re-solved; other logic/scope unchanged. Native target verification pending.

- V120 manual replacement: Z=-0.15m relative to same v117 reference, keep X=-0.034483846m and Y=+0.008140797m. This is 30cm backward vs v119 +15cm Z, not an incremental -15cm. Same native rotation-only layer, reference wrists orientations preserved; rendering unverified.

- User rolled back v120 to v119, then requested 10cm MORE. V121 is based on v119, net Z=+0.25m relative v117, X=-0.034483846m and Y=+0.008140797m unchanged. Both reference wrists +0.10m Z vs v119; same scope. Native rendering pending.

- Latest combined manual requests: X=0, Z BACK TO V119 (+0.15m), Y remains +0.008140797m, all relative v117. V122 incorporates both; the earlier pending +25cm version was not released. Compared with v119 only X changes. Native placement pending.

- User asks RIGHT walking hold X=-5, then immediately corrects to X=+5cm. V123 adds +0.05m anatomical-right offset to the native v117 right pose using a separate positive-lean rotation layer. Right Y/Z unchanged; left v122 X0/Y+.008140797/Z+.15m retained. Both wrists follow, same third-person standing moving scope/Ctrl+F8; native visible result pending.
