MovementLab v68 - correct camera/heading sign and prone camera handoff

v67 assumed native heading and world camera yaw had the same sign. Native DayZ camera code explicitly uses negative heading for world yaw. v68 converts that sign before compensating the camera offset, so native turning replaces the look offset instead of adding an unintended view rotation.

The separate third-person prone LR helper now uses the same handoff compensation and stationary head/camera bounds. Working DayZ 1.30 animation graphs, movement input/direction handoff, stationary head-only rules, speed/momentum settings, stance icons and MMG/SNAFU loadout are unchanged. No root orientation or camera world-matrix override.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Actual source math is checked against DayZ's negative-heading world-camera convention, including delayed updates and wraparound. Native compile and first/third-person movement playback still require local testing. The earlier v67 math tests used the wrong heading convention and did not prove runtime camera stability.
