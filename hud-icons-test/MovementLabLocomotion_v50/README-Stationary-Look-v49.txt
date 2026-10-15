v49 body direction correction
The body root orientation was being used in the camera/heading sign convention, causing opposite-side turns. Convert body orientation into the internal negative-camera-yaw convention when read, and convert back at the root output. Camera mouse sampling, world view, head input and animation graphs are unchanged.
Stationary non-aiming rules retained: head +/-90, camera +/-145 triggers full body toward captured direction, same-side signed path through rear crossing.
Physical-world body turn direction checked across 20 initial heading/direction combinations including +/-145 and +/-200 degrees. Native compile, visual direction, feet animation and smoothness still require local DayZ testing.
