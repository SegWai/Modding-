MovementLab separate viewmodel PROTOTYPE v1 (offline only)

Based on Revision49. Current movement builds are preserved.
F9: native first-person hip view / separate screen-rendered dummy model.
F10: cycle three framing presets (close, closer, wide diagnostic).
Start in first person, hold RMB for hip aim, then turn the mouse.
Quick RMB still toggles ADS; ADS/thirdperson/reload/obstruction/menu use native view.

This uses PlayerPreviewWidget.GetDummyPlayer, not another world NPC or another
playable player. Its overlay has fixed model orientation independent of camera
and mouse. Only this dummy gets the fixed aiming pose. World player still handles
movement, ammo, shots, recoil and inventory. The original is locally hidden only
while the overlay is ready; leaving restores it. Prototype is off initially.

NOT CLAIMED COMPLETE: native rendering, clipping/framing/lighting and dummy pose
must be confirmed in DayZ. Full separate reload/firing animation synchronization
is not implemented; weapon actions fall back to native view. No custom meshes or
UI assets required. No network deployment: multiplayer falls back to native.
No screen messages. Collect-Logs.cmd writes MovementLab-Viewmodel-Prototype-v1-Logs.zip.
