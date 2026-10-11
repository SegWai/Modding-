CROUCH PHYSICAL SLOWDOWN TEST V2

Extract whole ZIP into a fresh folder, close DayZ, keep Steam running, run Launch-Movement-Test.cmd.

Built directly from stable v10 Strafe Test v2. Restores normal crouch gait request 1.0. New OnPhysMove callback attempts to retain only 20% of pending horizontal travel while slow-crouching. Native animation playback stays unchanged. Shift fast crouch, standing behavior and crouch-exit rules remain. Rotation and vertical motion are not scaled. Applies only to the offline unparented local player, excludes interaction states and correction-sized jumps.

Mock tests verify 20% horizontal translation and exclusions, and previous controller regressions. Native callback execution, collision behavior and visible world-space speed MUST be tested in DayZ. Feet may slide because animation playback is unchanged. Stable baseline remains unchanged.
