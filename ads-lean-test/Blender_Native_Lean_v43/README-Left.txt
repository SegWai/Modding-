NATIVE IN-GAME LEFT LEAN — Blender 4.3.2

Frozen walking/aiming pose captured from the NPC, ID 60375_true.
All 114 joint origins are imported from DayZ. This is one instant in the
walking cycle, not a looping walking animation or a stationary pose.

The supplied weighted body is retargeted to those joint positions. Its
local bone axes differ from DayZ, so mesh bone rotations are fitted to the
captured landmarks, with inherited twist for single-child chains. Native
raw orientation matrices are preserved separately in the hidden CAPTURE
DATA collection and Native-Captures.json. Skin twist may differ from DayZ.

The schematic AK is positioned using the captured weapon transform. It
is a guide, not the original weapon mesh, so stock/grip dimensions may differ.

Select Armature, Pose Mode, select a bone and R to rotate. Frame 1 is the
capture. Send back the edited .blend to transfer the pose change to the mod.
Original rest skeleton and skin weights preserved; no gameplay files changed.
