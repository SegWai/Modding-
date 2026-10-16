MovementLab v72 - body-relative right-shoulder third-person camera

The native camera distance follows the look vector, orbiting around a stationary body. v72 counteracts that positional orbit in the camera pivot so the final camera origin stays behind the body's right shoulder while look orientation remains native. The native distance and collision prediction are retained. Right-shoulder selection is forced locally. The anchor applies consistently while stationary and moving, including the separate prone camera update path. First-person and ADS camera classes are untouched.

Native bone/stance anchors and crouch height adjustments are retained. User leaning still offsets the shoulder. Existing v71 movement/head look handoff, speeds, animation graphs, HUD stance icons and loadout remain unchanged.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Actual-source geometry and package checks pass. Native compilation, view transitions and collision response near walls still require local testing. Camera pivot compensation is new and cannot be validated against the DayZ renderer in this environment.
