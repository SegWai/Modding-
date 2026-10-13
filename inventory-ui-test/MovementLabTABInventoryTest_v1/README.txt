MovementLab reference-style TAB inventory test v1

Close DayZ. Extract the ENTIRE ZIP into a NEW folder. Steam must be running.
Run Launch-Movement-Test.cmd, then press TAB after spawning.
This is the same movement/HUDv2/SNAFU test with a separate inventory UI addon
loaded last. Existing movement, controls, speeds, camera and mission are unchanged.
The original versions remain separate. Collect-Logs.cmd creates
MovementLab-TAB-Inventory-v1-Logs.zip if something fails.

The reference image is the visual target: near-black cargo cells with thin grey
outlines, compact pale item names, native quantity text, and an equipment thumbnail
at the LEFT of the cargo grid. Equipped vest/backpack/pants sections are labeled
Chest Rig/Backpack/Pockets where the native owner is that actual equipped item.
Magazines show the native quantity conversion with maximum, e.g.30/30.
Capacity text uses the real occupied cargo-cell area and real capacity, e.g.6/40.
No inventory capacity, item dimensions, quantity or clothing values are changed.

The preview PNG is a CONCEPT, not a verified native screenshot. This first native
skin focuses on cargo panels/headers and the left equipment thumbnail. Native
vicinity, character/equipment placement and quickbar arrangement stay native.
The reference's four pockets and45 capacity are not faked if your gear differs.
Your current plate carrier may have no direct cargo: attach pouches or equip a
vest with cargo to see its grid. The UI never spawns substitute Tarkov gear/items.
Actual item previews are DayZ/SNAFU equipment, not copies of the screenshot models.

For local-player cargo, the whole grid is inset before native code measures cell
sizes. The root's pixel/relative units are preserved. Item previews and quantity
labels sit in the reserved column. Their drag/drop/hover events use the existing
native header/container handlers. Original grid drop/rotate/collapse/transfer
code is not replaced. Nearby/world containers keep native geometry with styling.
Decorative backgrounds and labels ignore mouse input.

On narrow panels or when a native spacer refuses the inset, the addon logs a
fallback and keeps themed native geometry rather than forcing broken hit areas.
That means the left thumbnail column may not appear on that layout. Native
scrolling, collapse, pointer picking and precise geometry must be verified in
DayZDiag; no Windows DayZ runtime exists in the cloud.

Checks completed: original method names/signatures, actual skin code translated
to C++ GUI mocks, inset-before-measurement and matching grid/drop origin, pixel
and relative units, real references/capacities, cached preview updates, native
callback bindings, decorative pointer flags, narrow/spacer/vicinity fallback,
PAA structure and PBO entries/footer. These do not establish native rendering or
native Enforce compilation. Take a full TAB screenshot after opening it, and
check dragging a magazine into cells, rotation, collapse and backpack scrolling.

InventoryUISource contains the new Mission-only client UI source and textures.
@MovementLabInventoryUI is its independent addon. To disable the UI test, remove
that final mod from the launcher's -mod list; the movement test remains intact.
Standalone installation details are in README-Inventory-Mod.txt.
