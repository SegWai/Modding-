MovementLab — video-reference walking revision v07

BLENDER REVIEW FIRST
Open TestAnimations/MovementLab_Unarmed_Walk_v07.blend in Blender 4.3.2.
Press Space. The saved view looks from the front, for comparison with the new reference.
The character walks in place. Orbit the view to inspect the side and rear.
No addon is required for playback. The bundle includes rear, side and front GIFs.
Blender playback loops frames 0–33. Frame 34 is a duplicate endpoint for TXA.

WHAT CHANGED FROM v06
- The toes rise to 22 degrees before heel placement (previously 14).
- Both landing knees are nearly straight (3 degrees of bend), through final
  reach and early double support. Supporting-knee flex starts after the other
  foot starts leaving the ground, then increases gradually.
- The ankle track narrows from 25 cm to 20 cm, bringing the legs closer.
- Arms sit farther out from the torso. Hand/finger mesh clearance from the
  hips measures 10.3-14.7 cm sideways through the loop on this reference body.

The pelvis height now follows supporting-leg extension while keeping its
vertical travel under 2 cm. The other leg's reach is also checked to avoid
stretching bones. Hands, ground clearance and replayed baked poses are
checked at integer and half frames. Clothing is absent from this reference
mesh; bulkier in-game clothing will need a separate clearance check.
This is original authored motion, not recovered Rockstar animation data.
The supplied reference videos and frames are not bundled.

WORKBENCH PREVIEW AFTER VISUAL REVIEW
Copy TestAnimations into D:\DayZProjects\MovementLabWorkbench.
The new names preserve the previous clips and preview files.
Restart Workbench through your configured shortcut.
In the main Resource browser expand:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v07.txa and use Reimport resource,
or Register resource and import if offered for the new resource.
Confirm a nonempty MovementLab_Unarmed_Walk_v07.anm is created beside it.
Source and metadata alone are not a compiled animation.

In Animation Editor use Workspace > Open, expand the tree, and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview_v07.aw
Select MovementLab_Walk_Preview_v07 under Anim Instances.
Filter walk, select an assigned walking animation cell, then choose the
compiled MovementLab_Unarmed_Walk_v07.anm in the editor File Browser.
Click Set Anim and Play. Filtering alone does not change its assignment.
Save only this separate preview instance/workspace, leaving vanilla files.

GAMEPLAY STATUS
This walking revision has not been compiled in Windows or tested in DayZ.
The existing arm-lift runtime test remains the working in-game diagnostic.
Native forward-walking slots, pace, footstep events and blends must be checked
before packaging a walking replacement. No walking PBO is included here.
Terrain, transitions, compatibility with other mods and multiplayer remain
untested. Judge this clip's motion in Blender before doing more game setup.

SOURCE AND NOTICES
Source/build_walk_clip_v07.py contains the authored cyclic key-pose curves.
It uses build_diagnostic_clip.py for argument parsing and bone-axis helpers.
validation.json records the authoring, bake, contact and TXA checks.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for the reference rig/exporter.
