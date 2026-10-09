MovementLab — video-reference walking revision v10

BLENDER REVIEW FIRST
Open TestAnimations/MovementLab_Unarmed_Walk_v10.blend in Blender 4.3.2.
Press Space. The saved view looks from the front, for comparison with the new reference.
The character walks in place. Orbit the view to inspect the side and rear.
No addon is required for playback. The bundle includes rear, side and front GIFs.
Blender playback loops frames 0–33. Frame 34 is a duplicate endpoint for TXA.

WHAT CHANGED FROM v09
- Vertical pelvis travel is reduced from about 1.92 cm to 1.16 cm (39 percent).
  The body stays more level through the supporting step instead of dipping
  with the previous fixed knee-bend curve. Legs accommodate the new height.
  Measured head bounce is also reduced by about 38 percent.
- The ankle track narrows from 20 cm to 16 cm, bringing the legs closer.

The sideways weight transfer is retained exactly: about 9.06 cm of lateral
pelvis travel, with the same supporting-side torso lean and timing as v09.
Shoulder/hip turns, inward forearm sweep, wrist/finger pose, small head tilt,
foot trajectory in the walking direction, foot pitch and cadence are retained.
The nearly straight landing knees and delayed initial support flex are kept.
Stance-leg flex is reduced as needed to support the more level body height.

Loop, bake, anatomical reach, foot contact, ground clearance and sampled 3D
hand-to-hip distance checks pass on the unclothed reference mesh. The latest
hip-surface check finds at least 9.4 cm of 3D distance; front-view projections
can still align because the hand is in front of the hip. Clothing and native
walking pace/blends remain Windows checks. No native Rockstar animation data,
source videos or frames are bundled.

WORKBENCH PREVIEW AFTER VISUAL REVIEW
Copy TestAnimations into D:\DayZProjects\MovementLabWorkbench.
The new names preserve the previous clips and preview files.
Restart Workbench through your configured shortcut.
In the main Resource browser expand:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v10.txa and use Reimport resource,
or Register resource and import if offered for the new resource.
Confirm a nonempty MovementLab_Unarmed_Walk_v10.anm is created beside it.
Source and metadata alone are not a compiled animation.

In Animation Editor use Workspace > Open, expand the tree, and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview_v10.aw
Select MovementLab_Walk_Preview_v10 under Anim Instances.
Filter walk, select an assigned walking animation cell, then choose the
compiled MovementLab_Unarmed_Walk_v10.anm in the editor File Browser.
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
Source/build_walk_clip_v10.py contains the authored cyclic key-pose curves.
It uses build_diagnostic_clip.py for argument parsing and bone-axis helpers.
validation.json records the authoring, bake, contact and TXA checks.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for the reference rig/exporter.
