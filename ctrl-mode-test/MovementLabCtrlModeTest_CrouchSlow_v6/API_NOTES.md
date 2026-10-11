CROUCH TEST V6 - COMPLETE ORIGINAL ANIMATION FOLDER

Close DayZ, keep Steam running, extract the entire ZIP into a fresh folder, run Launch-Movement-Test.cmd. No Addon Builder needed. The launcher runs Prepare-Crouch-Clips.ps1 first, reading D:\DayZProjects\DZ\anims\anm\player\moves\unarmed. It packages the complete folder into a LOCAL test PBO, retiming only six crouch-walk clips from 30 to 6 FPS. Original files remain unchanged.

Reason: v3 RPT proves many original clips under the overridden unarmed folder became unavailable. A complete local replacement should preserve them. The launcher checks each original clip reported missing in that log before packing. No custom animation profile, no physical scaling. Stable standing/controller scripts unchanged. Native folder override and timing still require game verification.

Windows PowerShell preparer is not executed in the Linux development environment. Stop and send the console error if preparation fails. Stable baseline remains unchanged.
