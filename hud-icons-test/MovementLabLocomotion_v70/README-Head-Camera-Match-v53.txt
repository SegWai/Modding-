v53 shared head/camera stop
The separate camera-only +/-90 numerical cutoff is removed. While stationary and not aiming, camera UpdateLRAngleUnlocked reads player.GetLookLimits and uses the matching left/right native look bounds, within native camera safety bounds. These engine look-limit values are not assumed to equal visually measured world yaw.
Native automatic free-look retains the body forward. No body rotation or custom camera matrix. Original native head animation and movement/aiming exit retained.
Logs report player look bounds, selected camera bounds, native yaw and rendered camera/body yaw. This establishes whether camera and head endpoints align in the actual game; no claim of a measured 90-degree visual stop until tested.
All other movement, graphics/graphs, weapon sway, HUD stance indicators and MMG/SNAFU loadout unchanged. Source/package checks passed; native compile and local head/camera endpoint verification pending.
