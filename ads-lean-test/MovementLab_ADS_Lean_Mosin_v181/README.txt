V181: SHARED APPROVED PRESETS / CLOSE CROUCH COMPARISON

Both uploaded JSON files are included byte-for-byte. MLLeanPreset.json is the
approved standing baseline. MLWalkingLeanPreset.json is the approved upright
walking/running baseline. Selection is native gait for EVERY offline PlayerBase,
including the selected player and other characters, not a special blue NPC.
First/third person share those values. Old learned172walking retarget and
NPC-specific157head matching no longer override the saved settings.
Crouching keeps the existing crouch base, rather than straightening its legs
with standing-only body edits. No new crouch preset has been authored here.

The old stationary and walking previews have been removed. Two NEW Denis NPCs
stand 0.5m centre-to-centre, 2m closer than the old2.5m spacing:
RED: crouched, weapon lowered (not aiming).
BLUE: crouched, weapon raised (not ADS).
Both read one clock: LEFT1sec, CENTRE1sec, RIGHT1sec, CENTRE1sec, repeat. Native
lean interpolation happens within each one-second target interval. No walking,
no recording/replay, no forced optics head tilt. ForceStance requests CROUCH;
raised-only presentation uses the established visual demo control. The old
canary no longer forces ADS graph routes. Actual native crouch/raised behavior
needs verification in DayZ, since this build has not been run on Windows.

Player AK74/SKS/Glock/backpack retained. CtrlF1 native comparison, CtrlF8 arm
comparison, X freeze and F6/F7 RMB navigation remain. F6/F7 still edit the walking
bank, now shared across characters when walking, not these stationary crouched
previews. Shared presets save at Profiles/LeanMosin/MLLeanPreset.json and
Profiles/LeanMosin/MLWalkingLeanPreset.json. Canonical saves still win on launch.
Use a fresh folder so older local saves do not replace the supplied uploads.

This is the offline test mission, not a multiplayer rollout. Exact native pose
matching across models/weapon classes, bank transitions, no-ADS crouch behavior,
hand grip and crash safety require in-game testing. No parameter zero reset.
