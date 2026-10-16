MovementLab v75 - retain posture/smoothing, remove look controller

Restores the v66 pose graph and its straight-shoulder correction, learned idle offset, continuous moving/stationary head-pose blending, smoothed movement-to-idle transition and immediate native combat ownership. The posture module now runs independently of camera/input control.

Only the look-controller behaviour is removed: no automatic free-look, custom head/camera angle limits, camera rotation/position overrides, forced root orientation or synthetic movement-look handoff. Native DayZ look and body-turn controls run normally. The graph's camera-driven extra head-yaw variable remains at its zero default; posture/smoothing layers are retained.

Speeds/momentum, stance HUD, sway changes and MMG/SNAFU loadout are preserved. Extract into a fresh folder and launch Launch-Movement-Test.cmd. Do not merge with a prior folder, which may retain older locking scripts.

Static pose/control-separation, graph/dependency and package integrity checks passed. Native DayZ compilation and playback remain untested here.
