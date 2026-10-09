MovementLab — video-reference walking revision v09

BLENDER REVIEW FIRST
Open TestAnimations/MovementLab_Unarmed_Walk_v09.blend in Blender 4.3.2.
Press Space. The saved view looks from the front, for comparison with the new reference.
The character walks in place. Orbit the view to inspect the side and rear.
No addon is required for playback. The bundle includes rear, side and front GIFs.
Blender playback loops frames 0–33. Frame 34 is a duplicate endpoint for TXA.

WHAT CHANGED FROM v08
- During the forward swing, only the elbow-down segment sweeps inward toward
  the pelvis, by up to 20 degrees. It opens back out on the backward swing.
- A small forearm pronation (up to 2.5 degrees) adds a slight natural tilt.
  The existing wrist keys and static relaxed finger pose are retained.
- Hip and shoulder/chest rotation are approximately 40 percent stronger.
- Weight transfer is heavier: the pelvis shifts about 9 cm side to side,
  compared with roughly 5.6 cm in v08. The torso leans farther onto support.

The latest request brings the forward hands near the outer hip line; their
old 10-15 cm sideways gap is therefore no longer held on the forward swing.
Hands can align with hips in a front-view projection while staying in front
of them. A 3D polygon-surface check finds at least 8.7 cm between hand/finger
vertices and the hip band through half-frame samples on this reference mesh.
This is a sampled mesh check, not a native clothing collision test.

The raised toes, nearly straight landing knees, delayed support-knee flex,
20 cm ankle track, regular 34-frame cadence and small head tilt are retained.
Vertical pelvis travel stays below 2 cm despite the stronger sideways shift.
No independent finger tics or irregular step patterns are added.
No native Rockstar animation data, source videos or frames are bundled.

WORKBENCH PREVIEW AFTER VISUAL REVIEW
Copy TestAnimations into D:\DayZProjects\MovementLabWorkbench.
The new names preserve the previous clips and preview files.
Restart Workbench through your configured shortcut.
In the main Resource browser expand:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v09.txa and use Reimport resource,
or Register resource and import if offered for the new resource.
Confirm a nonempty MovementLab_Unarmed_Walk_v09.anm is created beside it.
Source and metadata alone are not a compiled animation.

In Animation Editor use Workspace > Open, expand the tree, and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview_v09.aw
Select MovementLab_Walk_Preview_v09 under Anim Instances.
Filter walk, select an assigned walking animation cell, then choose the
compiled MovementLab_Unarmed_Walk_v09.anm in the editor File Browser.
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
Source/build_walk_clip_v09.py contains the authored cyclic key-pose curves.
It uses build_diagnostic_clip.py for argument parsing and bone-axis helpers.
validation.json records the authoring, bake, contact and TXA checks.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for the reference rig/exporter.
