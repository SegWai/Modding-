MovementLab v65 - animation graph compatibility repair attempt

The uploaded v64 workspace PBO passed its SHA1 check, and all graph/template patches matched the distributed source. Logs confirm scripts compiled, then the animation graph failed to load at CroMoveLowG before player spawn. The exact native loader rejection is not exposed by these logs.

Targeted repair: four moving head-look blends now reference the original native head Pose2 directly rather than the procedural stationary head-rotation wrapper. The stationary extra head rotation and shoulder correction remain. Custom rotation item formatting follows native multiline syntax. This keeps the stationary procedural rotation out of the moving crouch graph dependency path.

The v64 movement-direction handoff and camera limits are retained unchanged. Other movement speeds, momentum, HUD icons and MMG/SNAFU loadout are retained.

Extract into a fresh folder and launch Launch-Movement-Test.cmd so the workspace PBO rebuilds. Static source/dependency and PBO/ZIP integrity checks passed. This is a targeted compatibility attempt, not a confirmed native crash fix; DayZ native graph loading and movement playback cannot be tested in this environment.
