MovementLab v64 - stationary looking and movement handoff

Stationary non-aiming head-only look is retained. Any movement input releases automatic free-look and transfers the current camera yaw to native aim input once, so normal movement uses the looked-at direction. The old camera yaw offset is cleared once to avoid applying the turn twice. No root teleport, forced orientation or custom HeadingModel is used.

Camera yaw is limited to +/-100 degrees: the head-only pose ends at +/-90 and the retained procedural extension adds 10. The former +/-170 camera range allowed looking behind after the head pose stopped.

Unchanged: animation graphs, native moving shoulder poses, continuous head blending, idle shoulder correction, combat/aim safeguards, speed and momentum settings, stance icons, MMG/SNAFU loadout.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Native compile and in-game validation are pending. Test left/right stationary look stops, then W/A/S/D and diagonals from either side in first/third person, standing/crouching/prone. Check that movement faces the previous look direction without a camera recenter or duplicate turn, and that stopping restores stationary head-only looking.
