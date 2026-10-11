CROUCH WHEEL TEST V1 - EXPERIMENTAL

Close DayZ, keep Steam running, extract ALL files to a fresh folder and run Launch-Movement-Test.cmd. It builds two local PBOs from your complete unarmed and player_main folders under D:\DayZProjects\DZ\anims. Original files remain unchanged.

Crouch: wheel up increases level, down decreases. Starts at 1, remembers selection across crouch exits. Levels: 1=20% of original slow crouch clip pace, 2~47% (nearest integer FPS to 45%), 3=60%, 4=80%, 5=native fast crouch like Shift. Lower tiers are relative to slow crouch, not fast crouch. Holding Shift temporarily selects original fast crouch. Standing rules and stable strafe rules remain.

This edits the template, main graph variable, locomotion selection and instance mappings. No engine-level live FPS setter is assumed. Retimed clip groups are selected by a graph variable. Native graph loading/binding is UNVERIFIED. The script log prints [MovementLab Wheel] Graph variable binding; -1 means failed.

Wheel uses native previous/next-action inputs in this prototype; other mouse-wheel action selection can still react. Test away from interactable items. Raised/injured crouch retains native paths. F7 changes controller only, not the loaded graph.

Windows preparation and native DayZ compilation/animation require your test. Stable v10 Strafe Test v2 is unchanged.
