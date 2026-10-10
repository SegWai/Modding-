# v7: four crouch rules directly on approved v4

Source directory was copied from stable Ctrl Modes v4 direction fix. No v5/v6
logic is used. Standing filter method is byte-identical to v4. The original
command startup/mode body remains, with crouch processing before it and a
Ctrl exception only for the Shift hold consumed by a fast-crouch exit.

MovementLabUpdateCrouchRules runs before both World and mission movement
processing so a stance edge is resolved regardless of callback order. Common
eligibility keeps controls local/offline/standing or crouched, and excludes
UI, pause, invalid commands, aiming, gestures, unconscious/dead states and
large timesteps. Other stances continue through original v4 cancellation.

Slow crouch requests gait 1 only with movement. Shift releases that speed
ownership to native DayZ, preserving its original fast crouch and directional
limits. Idle Shift never produces movement. No angle override is added in
crouch. The mission cancels standing braking before refreshing crouch rules
so it cannot erase slow crouch ownership or pin a standing stopping angle.

m_MovementLabFastCrouch describes CURRENT crouch Shift+movement, not whether
Shift was ever used during crouch. On an erect edge, fast selects saved jog;
slow leaves the saved standing walk/jog mode untouched. An existing fast-crouch
Shift hold is consumed for upright movement until release, making the exit
jogging rather than sprinting. Wanted gait thereafter behaves like v4 once
Shift is newly pressed. Ctrl can select walk even while that consumed hold
continues. Resetting prior wanted gait on the crouch exit prevents a phantom
standing deceleration from native fast crouch. Mode-return/stop curves retain
v4 durations and direction fixes. Camera and native graphs are unchanged.

Actual translated World and mission checks at 30/60/144 FPS and both callback
orders cover all four rules over previous walk/jog mode and eight directional
masks. Shift release before/after/same-frame standing, idle Shift, crouching
mid-standing brake, new standing sprint requests, Ctrl after fast exit and
prone/disabled paths are checked. Fast crouch leaves speed/angle overrides
absent; raw native-input fallback models uncapped control, not measured
physical speed. Existing standing/start/stop/back-diagonal tests also pass.
Native Enforce compilation, animation frames and physical paths need DayZ.
