MovementLab — video-reference walking revision v04

BLENDER REVIEW FIRST
Open TestAnimations/MovementLab_Unarmed_Walk_v04.blend in Blender 4.3.2.
Press Space. The saved view looks from behind, like the supplied reference.
The character walks in place. Orbit the view to inspect the side and front.
No addon is required for playback. The bundle includes rear, side and front GIFs.
Blender playback loops frames 0–34. Frame 35 is a duplicate endpoint for TXA.

WHAT THE VIDEO GUIDED
The requested reference is the TOP character's walking animation:
https://www.youtube.com/shorts/FJnBXvfNc_E
The supplied crop is a 5.02-second rear view at 60 fps.
A repeating lower-body pattern suggests a cycle around 1.17 seconds.
This study uses a 35-frame cycle at 30 fps (1.167 seconds).

The hips lead the weight transfer; shoulders and arms follow with delayed,
overlapping curves. Elbows and wrists have separate timing, with slight
sideways hand travel and relaxed fingers. The head orientation stays quiet.
The smaller body dip and straighter supporting leg from v03 are retained.

This is an original, manually authored interpretation of visible motion.
The camera is behind the character and follows him. Some foot contacts are
cropped at the bottom, and forward/back depth is obscured. Joint angles,
stride depth and absolute speed therefore cannot be measured exactly from
this one view. The nominal 0.90 m/s is an authoring choice, not measured video
speed. reference_notes.json distinguishes observations from authored choices.
No native Rockstar animation data, video frames or assets are bundled.

WORKBENCH PREVIEW AFTER VISUAL REVIEW
Copy TestAnimations into D:\DayZProjects\MovementLabWorkbench.
The new names preserve the previous clips and preview files.
Restart Workbench through your configured shortcut.
In the main Resource browser expand:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v04.txa and use Reimport resource,
or Register resource and import if offered for the new resource.
Confirm a nonempty MovementLab_Unarmed_Walk_v04.anm is created beside it.
Source and metadata alone are not a compiled animation.

In Animation Editor use Workspace > Open, expand the tree, and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview_v04.aw
Select MovementLab_Walk_Preview_v04 under Anim Instances.
Filter walk, select an assigned walking animation cell, then choose the
compiled MovementLab_Unarmed_Walk_v04.anm in the editor File Browser.
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
Source/build_walk_clip_v04.py contains the authored cyclic key-pose curves.
It uses build_diagnostic_clip.py for argument parsing and bone-axis helpers.
validation.json records the authoring, bake, contact and TXA checks.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for the reference rig/exporter.
