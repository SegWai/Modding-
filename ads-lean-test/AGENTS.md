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
