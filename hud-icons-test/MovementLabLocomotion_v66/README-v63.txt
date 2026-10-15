MovementLab v63 - restore native moving shoulder poses

Fixes the v62 regression that applied the stationary shoulder trim to upright movement.
The original moving arm IK node is restored. Shoulder trim now affects only the stationary idle branch.
The learned idle offset stays primed for stopping; it does not rotate the moving pose.
Continuous head-look blending, stationary head/camera limits, combat safeguards, locomotion speeds, momentum, stance indicators and MMG/SNAFU loadout are retained.

Extract to a new folder and launch with Launch-Movement-Test.cmd. Do not run another test version alongside it.
Static graph/source checks and PBO/ZIP integrity checks passed. Native DayZ compilation and in-game behaviour require local testing.
