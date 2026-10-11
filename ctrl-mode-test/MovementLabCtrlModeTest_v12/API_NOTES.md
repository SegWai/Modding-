# Pure strafe resistance test

Based on Ctrl Modes v11. Pure jogging A/D reversals now use OverrideMovementSpeed with a continuous blended gait request. Resistance lasts 0.50 seconds and refreshes on opposite key edges. Speed decreases at at most 5 gait units/second and increases at at most 3.5. No direction override, pose freezing or command restart is introduced. Native directional filtering remains from v11.

Existing mission braking is the sole stop owner. Walking, sprint requests, crouch, startup, braking and interaction exclusions reset the new gait state. A/D overlap preserves the current request; no-key release hands control to existing stopping.

Translated actual script checks passed at 30/60/144 FPS in both callback orders, including resistance recovery and spam slew limits. Native Enforce compilation and native animation/physics validation remain pending.
