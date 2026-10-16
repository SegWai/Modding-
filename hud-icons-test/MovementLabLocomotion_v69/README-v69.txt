MovementLab v69 - retain actual world view during movement handoff

Captures the current rendered camera world yaw when movement starts. Camera compensation is calculated against the native heading model passed back to the engine, instead of assuming raw input heading is the rendered heading. Normal mouse delta updates the held world direction during the transition. On movement entry, the complete free-look pitch is promoted to the normal camera pitch so native additive-angle return smoothing cannot tilt the view back toward the old pitch. The 500ms automatic recenter and handoff-angle clamp are removed; compensation ends when actual heading alignment makes the camera offset zero. Combat still returns to native controls.

HeadingModel is observed after the native implementation; its heading/orientation values and return value are not modified. The working 1.30 animation graphs are unchanged. Standing/crouch stationary head-only rules and prone helper, movement speeds, momentum, HUD stance icons and loadout remain.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Static actual-source math and package integrity checks pass. Native compile and playback remain untested here. Logs now record held world yaw, engine heading, raw input heading and remaining camera offset so any further drift can be traced against the video.
