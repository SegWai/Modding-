# Reference-style TAB inventory test v1

The user requested a DayZ TAB inventory HUD based on a dark vest/chest-rig/
backpack screenshot, with a picture first. The published preview is
`MovementLab_TAB_Inventory_Concept_v1.png`, a generated concept, not native output.
It was linked during implementation before coding was completed.

New addon source: `inventory-ui-test/MovementLabTABInventoryTest_v1/InventoryUISource`.
The standalone Mission-only client addon has prefix MovementLabInventoryUI.
It neither depends on SNAFU nor changes item definitions/gameplay. The full test
loads it after the unchanged HUDv2/movement/SNAFU demo modules.

Implemented appearance layer:

- Dark outlined native cargo cells and native headers.
- Compact names on cargo/hands items; native magazine quantity text with maximum.
- A native item preview and real used/total cargo-cell capacity left of eligible
  local-player cargo grids. Equipped vest/backpack/pants use Chest Rig/Backpack/
  Pockets titles; other containers retain their actual display names.
- Cached preview binding, existing native header drag/drop/hover handlers, and
  pointer-ignoring decorations. Original drop, rotation, transfer and collapse
  code is retained.

The complete cargo root is inset before native code initializes/measures row
cells. Its original horizontal pixel/relative units are preserved to respect
native SizeToChild/SizeToParent scripts. The sidebar cannot be forced on layouts
that refuse its offset or are too narrow; they keep themed native geometry and
log the fallback. Real equipped items, footprints and capacities are retained,
including gear with no direct cargo. No screenshot quantities or Tarkov models
are manufactured as actual inventory data.

This first skin targets the reference's cargo-panel arrangement. It does not
implement the entire preview's center equipment arrangement or a fake empty
vicinity grid. Those regions and the quickbar retain native layout. Exact native
pixel matching/clip behavior and native Enforce compilation are unverified,
since native GUI layouts and Windows DayZ runtime are not available in cloud.

Checks:

- Native method/signature matches and use of verified widget/layout class names.
- Actual skin code translated to C++ with native GUI mocks: before-initialization
  inset, matching drop origin, relative/pixel units, native quantity references,
  header callback bindings, cached model updates and fallbacks.
- Byte comparison of preceding World, Mission, HUD and workspace resources.
- PAA resource decoding by independent armake reader.
- Inventory PBO header, source-entry bytes, offsets and SHA1 footer; ZIP integrity.

The mock checks do not establish native compilation/rendering or actual drag/drop.
User test: open TAB, take a full screenshot, move and rotate a magazine, collapse
containers and scroll backpack cargo. Logs: MovementLab-TAB-Inventory-v1-Logs.zip.

Artifacts:

- MovementLab_TAB_Inventory_Test_v1.zip: complete offline test.
- MovementLab_TAB_Inventory_Mod_v1.zip: independent UI addon/source/preview.

Previous versions and the user's preexisting untracked arm-lift assets are retained.
