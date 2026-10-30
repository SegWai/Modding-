MovementLab v77 - native turn-in-place threshold 90 degrees

Sets SHumanCommandMoveSettings.m_fTurnAngle to 90 after native movement settings initialize. The documented native unit is degrees and the default is 45. This changes the native left/right turn-in-place trigger; it does not add camera locks, forced free-look, custom root rotation or input injection.

All v76 gameplay scripts, posture/turn smoothing graph, native turn clips, walking/jogging/running settings, speed profiles, HUD and weapon selection are retained unchanged. Moving alignment still uses its existing native movement filters.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Initialization logs show the threshold being set. Static SDK/source and package checks passed; native compilation and the exact in-game trigger/feel require local testing.

Loadout attachment selection now prioritizes compatible real suppressors in muzzle/suppressor slots and excludes bottle/improvised suppressors on every pass. Uses installed native/SNAFU classes and actual engine attachment acceptance. Weapons without a compatible installed suppressor retain another accepted muzzle attachment or an empty slot; no incompatible suppressor is forced. Existing full attachments and ten spare magazines per weapon remain.
