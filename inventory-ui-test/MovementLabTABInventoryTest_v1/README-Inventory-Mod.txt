MovementLab TAB inventory appearance addon v1

Copy @MovementLabInventoryUI beside your other mod folders. Add its full path
at the END of your launcher -mod list, or load it through the DayZ launcher.
For example: -mod=@YourExistingMods;@MovementLabInventoryUI
This client Mission-only addon requires native DZ_Data and DZ_Scripts. It does
not require SNAFU, MovementLab movement scripts or the custom stance HUD.
It does not spawn gear, alter character state or change cargo capacities.
The complete test ZIP loads it alongside the existing offline test as a convenience.

Dark outlined cells, compact item names, native magazine current/max text and
actual equipment preview/capacity column are the reference-style target.
Only actual locally owned cargo receives an inset column; native quantities,
item footprints, vicinity/equipment arrangement and quickbar remain intact.
Narrow/spacer-controlled panels fall back to themed native geometry.

The included preview is a DESIGN CONCEPT. Exact native layout/pixel matching,
Enforce compilation, dragging, rotation, collapsing and scrolling require a
local DayZ test. Do not treat C++ mocks as a native playtest.
If using a server, follow its existing client-mod/signature rules. This package
contains no signatures and is prepared for the user's offline DayZDiag test.
