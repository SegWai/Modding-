MovementLab v73 - fixed-position pivot prototype, based on v71

Chosen behaviour: while stationary, looking left/right rotates the view from the same point rather than orbiting around the body. During movement the camera follows character translation with its captured offset held in world axes, so body rotation does not swing the camera origin around the character. Native forward framing is captured on camera activation; no forced right-shoulder offset or body-relative anchor from v72 is included.

The native camera look orientation, head limits, v71 movement/head handoff and DayZ 1.30 animation graphs are unchanged. Native camera distance and collision prediction remain enabled. Stance/camera changes recapture the native framing. Crouch is anchored after its existing height correction. This experiment applies to third-person non-aiming standing/crouch/prone; first-person and raised/ADS camera behaviour remain native.

Extract to a fresh folder and launch Launch-Movement-Test.cmd. Test standing still and looking left/right first, then starting/stopping movement without mouse input. Native renderer, camera blending and collision response near walls are not available for verification here. This is a fixed-pivot prototype, not a confirmed in-game camera fix.
