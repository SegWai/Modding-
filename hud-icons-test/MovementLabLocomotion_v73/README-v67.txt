MovementLab v67 - prevent camera reset on movement handoff

The v64-v66 handoff cleared the free-look camera offset on the command frame, even if native heading had not yet applied the transferred turn. v67 keeps the residual camera offset until the measured native heading has replaced it, preserving world view across command/camera update order. Turning beyond the transferred angle remains normal mouse movement. A 500ms timeout and combat interruption release compensation into native return smoothing without clearing the camera angle.

The working v66 DayZ 1.30 animation workspace, movement direction handoff, stationary camera/head bounds, shoulder fixes, speeds, momentum, stance HUD and loadout are retained. No animation graph changes.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Static source, actual handoff-math harness and package integrity checks passed. Native DayZ compile/playback and first/third-person transition feel require local testing.
