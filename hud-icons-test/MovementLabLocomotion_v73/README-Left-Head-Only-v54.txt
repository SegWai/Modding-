v54 left shoulder/torso look test
While stationary and not aiming, measured left camera yaw selects the existing native MoveHeadLookPose (Locomotion.Cro.MoveLookHead), which DayZ already uses for head looking while sprinting. It replaces only the stationary idle look additive source during left look. At right/centre, movement, aiming and actions, the original native LookInjBlend is selected unchanged.
The same stock head pose is used as the experimental left-look replacement across stationary stances; pose compatibility and whether it fully removes the reported shoulder movement must be tested locally. No guarantee that the stock source contains zero torso motion until runtime checked.
Camera limit/update method unchanged from v53. No body-heading, camera-matrix or speed changes. MMG/SNAFU loadout and HUD retained.
Fresh extraction required so the launcher rebuilds the workspace PBO. Graph variable/source names and unique nodes checked; native compile/animation validation pending.
