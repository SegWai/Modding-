MovementLab: isolated Animation Editor preview

Prerequisite: Workbench has created MovementLab_ArmLift_Test.anm from the TXA.
This package contains two new text files, not another animation export.
Their compatibility with the user's editor still needs testing.

1. Extract this ZIP. Copy its two TestAnimations files into the existing folder:
   D:\DayZProjects\MovementLabWorkbench\TestAnimations
2. Open Animation Editor from the main Workbench window's Editors menu.
3. Use Workspace > Open. In the internal picker navigate:
   Game Root > MovementLabWorkbench > TestAnimations
   Choose MovementLab_ArmLift_Preview.aw.
4. Select MovementLab_ArmLift_Preview under Anim Instances.
5. In Anim Sets, filter for "walk". Select an assigned walking-animation cell,
   like the one used for the earlier vanilla walking playback test.
6. In Animation Editor's File Browser, select (single-click) the compiled:
   Game Root > MovementLabWorkbench > TestAnimations > MovementLab_ArmLift_Test.anm
7. Click Set Anim, then press the preview Play button.
   Expected: right arm rises and returns over approximately four seconds.

The new ASI inherits vanilla default assignments. Set Anim adds the test
assignment to this new instance. Select MovementLab_ArmLift_Preview before
changing an assignment. This allows testing without writing the vanilla ASI.
No template or graph edits are needed for this preview.

If opening the AW fails, capture the console error. If Set Anim is disabled,
capture the complete Animation Editor window so the selected cell and source
file are visible. If playback looks distorted, capture a representative pose.

This AW is an editor-only test. The absent event table is deliberately omitted,
as in the user's existing working preview. It is not a gameplay workspace and
does not establish runtime or multiplayer compatibility.

These files reference the user's extracted DayZ resources. They contain no
copied vanilla animation data or graph definitions. GUIDs on existing resources
are preserved from the user's working player workspace. Workbench may generate
resource identifiers for the two new files when they are registered.
