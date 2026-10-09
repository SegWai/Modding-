MovementLab — original unarmed walking study v01

FIRST CHECK: BLENDER
Open TestAnimations/MovementLab_Unarmed_Walk_v01.blend in Blender 4.3.2.
Press Space to play. The character walks in place, with alternating steps,
hip weight shifts and opposing arm swing. Frames 0–35 form the playback loop;
frame 36 duplicates the first pose for the TXA export. No addon is needed
to play this Blender file. preview_walk.gif also shows the loop.

SECOND CHECK: DAYZ ANIMATION EDITOR
Copy this bundle's TestAnimations folder into:
  D:\DayZProjects\MovementLabWorkbench
Keep the existing arm-lift files. These new files have different names.
Restart Workbench through your existing configured shortcut.
In the main Workbench Resource browser open:
  Game Root > MovementLabWorkbench > TestAnimations
Right-click MovementLab_Unarmed_Walk_v01.txa and choose Reimport resource,
or Register resource and import if this resource is not registered yet.
Confirm a nonempty MovementLab_Unarmed_Walk_v01.anm appears beside the TXA.
The ZIP contains source and metadata, not a compiled ANM.

In Animation Editor, Workspace > Open, expand the folder tree and select:
  Game Root > MovementLabWorkbench > TestAnimations > MovementLab_Walk_Preview.aw
Choose the MovementLab_Walk_Preview instance under Anim Instances.
Filter walk in Anim Sets, select an assigned walking animation cell, then
select MovementLab_Unarmed_Walk_v01.anm in the editor's File Browser.
Click Set Anim and Play. Filtering walk alone does not assign the new clip.
Save only this separate preview workspace/instance; leave the vanilla files.
Check the body shape, alternating steps, and the wrap between loops.

GAMEPLAY CHECK COMES AFTER PREVIEW
This is an original motion study with a nominal 1.2-second cycle and
0.80 m/s authoring reference. It does not change DayZ's movement speed.
The root stays stationary: stance feet move backward relative to the body,
matching hypothetical forward travel at that reference speed on level ground.
Standing still in the editor therefore looks like walking on a treadmill.
The validation checks contact drift with that hypothetical travel, not
contact in the running game. The exported TXA includes a duplicate endpoint;
native imported timing must also be checked before matching gameplay pace.

Before an in-game walking replacement, inspect the installed forward unarmed
walking assignment and its timing. Do not replace every walking direction,
crouch, weapon, or running slot with this one forward study. Keep the working
arm-lift runtime mod as-is for now. No walking PBO is supplied in this bundle.
Footstep events, heel/toe roll, slopes, transitions, other mods, multiplayer,
and native movement-speed matching remain untested.

SOURCE AND NOTICES
Original procedural keyframes are in Source/build_walk_clip.py. It uses
Source/build_diagnostic_clip.py for shared argument and bone-axis helpers.
validation.json records the cloud authoring/export checks; Windows Workbench
compilation and gameplay playback of this walking clip are still pending.
See ASSET_NOTICES.txt and EXPORTER_LICENSE.txt for reference rig/exporter terms.
No Rockstar animation assets are included.
