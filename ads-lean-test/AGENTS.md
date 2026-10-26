# Lean-test package preferences

- Launch lean-test batches directly. Do not add numbered native/custom menus or `choice` prompts. Keep the native/custom comparison in-game on F7 and explain the in-game keys to the user.
- The user's menu request applied only to the separate FPS graphics-settings helper. Preserve its apply/restore menu.
- Use `F:\DayZProjects` as the default project root in new packages. Treat the Steam game-install directory as a separate path.

- Apply pose and animation corrections through the shared player/NPC graph so identical stance, gait and lean inputs receive identical corrections; do not add NPC-only pose changes.
- Keep the approved custom raised-weapon pose in both first and third person, including aiming without ADS. Fix snapping by smoothing transitions; do not restore default first-person animations or restrict the custom raised pose to third person.
- Future mod test ZIPs must contain only runtime/diagnostic essentials (PBOs, mission, launcher, log collector, required manifests and short instructions). Do not include Blender files, templates, clips, previews, importers or Blender build helpers. Keep authoring data and source in the repository rather than the runtime ZIP.
