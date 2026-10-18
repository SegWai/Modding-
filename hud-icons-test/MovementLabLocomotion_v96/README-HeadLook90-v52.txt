v52 early/asymmetric camera-stop test
Removes the extra per-player SetLookLimits +/-90 restriction added by v51. Native stationary free-look and the native camera yaw clamp +/-90 are retained; no body rotation, custom camera matrix, heading accumulator or graph changes.
Every 500ms while active, logs native camera yaw and independently measured rendered world-camera yaw relative to the character root, plus body/input heading. A rendered frame may lag the current native angle while moving; check the settled endpoint. These readings are needed to establish the actual left/right limits; screenshots alone cannot establish exact angles.
Movement, sway, stance icons, graphs and MMG/SNAFU loadout unchanged from v51/v42 baseline. Native compile and actual endpoint testing remain pending.
