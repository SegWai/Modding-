# Lean-test package preferences

- Launch lean-test batches directly. Do not add numbered native/custom menus or `choice` prompts. Keep the native/custom comparison in-game on F7 and explain the in-game keys to the user.
- The user's menu request applied only to the separate FPS graphics-settings helper. Preserve its apply/restore menu.
- Use `F:\DayZProjects` as the default project root in new packages. Treat the Steam game-install directory as a separate path.

- Apply pose and animation corrections through the shared player/NPC graph so identical stance, gait and lean inputs receive identical corrections; do not add NPC-only pose changes.
- Keep the approved custom raised-weapon pose in both first and third person, including aiming without ADS. The latest user request removes added animation smoothing: do not reintroduce lean/raise/gait easing without a new request. Preserve the fixed wrist-bound first-person camera and native game animation timing; do not restore default first-person poses or restrict custom raised posing to third person.
- Future mod test ZIPs must contain only runtime/diagnostic essentials (PBOs, mission, launcher, log collector, required manifests and short instructions). Do not include Blender files, templates, clips, previews, importers or Blender build helpers. Keep authoring data and source in the repository rather than the runtime ZIP.
- For lean-distance balancing, use measured original DayZ distances from the same standing/weapon/aiming state as the target, rather than inventing a centimetre value. Keep the custom silhouettes similar and feet planted. Report any meaningful vanilla left/right asymmetry before choosing a shared symmetric target.
- Latest target: standing raised/aimed head travel from neutral is 42 cm character-left and 21.9 cm character-right. This supersedes the symmetric 32 cm root-centre target. Preserve earlier approved pose style, planted feet, walking/crouching and first-person behaviour.
