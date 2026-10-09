MovementLab — video-reference walking revision v08

BLENDER REVIEW FIRST
Open TestAnimations/MovementLab_Unarmed_Walk_v08.blend in Blender 4.3.2.
Press Space. The saved view looks from the front, for comparison with the new reference.
The character walks in place. Orbit the view to inspect the side and rear.
No addon is required for playback. The bundle includes rear, side and front GIFs.
Blender playback loops frames 0–33. Frame 34 is a duplicate endpoint for TXA.

WHAT CHANGED FROM v07
- Hips rotate with the legs: the side with the forward leg comes forward;
  the side with the backward leg moves back.
- Chest and shoulders rotate with the opposing arms. Each shoulder follows
  its arm's forward/back swing, instead of relying on a separate small sway.
- A tiny additional forward/back and sideways head tilt is layered onto the
  existing head motion. Each additional tilt stays below one degree.

The 34-frame walking cadence remains unchanged. No irregular step pattern,
new wrist motion or finger/hand micro animation has been added. Fingers keep
v07's static relaxed pose; the existing wrist curves are retained.
The higher toes, nearly straight landing knees, delayed support flex and
20 cm ankle track from v07 are retained. The arms compensate for shoulder
turning to keep roughly 10-16 cm lateral hand-to-hip clearance through the
loop on the unclothed reference body. Clothing needs a separate native check.
The pelvis follows leg extension with under 2 cm vertical travel.

validation.json includes checks that hip rotation follows the feet and
shoulder rotation follows the hands, along with contact, clearance, loop,
bake and TXA checks. These checks do not establish visual naturalness.
No native Rockstar animation data, source videos or frames are bundled.

WORKBENCH PREVIEW AFTER VISUAL REVIEW
Copy TestAnimations into D:\DayZProjects\MovementLabWorkbench.
The new names preserve the previous clips and preview files.
Restart Workbench through your configured shortcut.
In the main Resource browser expand:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v08.txa and use Reimport resource,
or Register resource and import if offered for the new resource.
Confirm a nonempty MovementLab_Unarmed_Walk_v08.anm is created beside it.
Source and metadata alone are not a compiled animation.

In Animation Editor use Workspace > Open, expand the tree, and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview_v08.aw
Select MovementLab_Walk_Preview_v08 under Anim Instances.
Filter walk, select an assigned walking animation cell, then choose the
compiled MovementLab_Unarmed_Walk_v08.anm in the editor File Browser.
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
Source/build_walk_clip_v08.py contains the authored cyclic key-pose curves.
It uses build_diagnostic_clip.py for argument parsing and bone-axis helpers.
validation.json records the authoring, bake, contact and TXA checks.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for the reference rig/exporter.
