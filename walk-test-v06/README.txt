MovementLab — video-reference walking revision v06

BLENDER REVIEW FIRST
Open TestAnimations/MovementLab_Unarmed_Walk_v06.blend in Blender 4.3.2.
Press Space. The saved view looks from the front, for comparison with the new reference.
The character walks in place. Orbit the view to inspect the side and rear.
No addon is required for playback. The bundle includes rear, side and front GIFs.
Blender playback loops frames 0–33. Frame 34 is a duplicate endpoint for TXA.

WHAT CHANGED
This version also uses the supplied three-second front-view John Marston clip.
The body shifts toward the supporting leg, with a restrained chest turn.
Shoulders rise/fall and follow arm swing separately. Arms hang closer to the
body, with smaller swing and softer elbow overlap than v05. The small body
dip is retained. The loop is 34 frames at 30 fps (1.133 seconds).

This is original manually authored motion, not motion capture. The front
clip is 240 x 512 pixels, with clothing obscuring joints and a tracking camera.
It shows a different character/reference from the earlier top-character video.
The two views are qualitative references, not synchronized camera views.
Depth, joint angles and nominal 0.90 m/s speed remain authoring estimates.
No source video, frames or Rockstar animation assets are bundled.

WORKBENCH PREVIEW AFTER VISUAL REVIEW
Copy TestAnimations into D:\DayZProjects\MovementLabWorkbench.
The new names preserve the previous clips and preview files.
Restart Workbench through your configured shortcut.
In the main Resource browser expand:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v06.txa and use Reimport resource,
or Register resource and import if offered for the new resource.
Confirm a nonempty MovementLab_Unarmed_Walk_v06.anm is created beside it.
Source and metadata alone are not a compiled animation.

In Animation Editor use Workspace > Open, expand the tree, and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview_v06.aw
Select MovementLab_Walk_Preview_v06 under Anim Instances.
Filter walk, select an assigned walking animation cell, then choose the
compiled MovementLab_Unarmed_Walk_v06.anm in the editor File Browser.
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
Source/build_walk_clip_v06.py contains the authored cyclic key-pose curves.
It uses build_diagnostic_clip.py for argument parsing and bone-axis helpers.
validation.json records the authoring, bake, contact and TXA checks.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for the reference rig/exporter.
