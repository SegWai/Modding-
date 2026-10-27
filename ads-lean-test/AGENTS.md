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
