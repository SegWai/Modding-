v56 arm/forearm crossfade
Keeps the working v54/v55 left head-only and original right poses. Widens angular crossfade from 8 to 24 degrees on the left of centre; increases critical damping from 0.18 to 0.35 seconds; limits blend speed and explicit per-frame weight changes to 1.6/second. Rapid reversals retain current blend weight/velocity. This slows the full pose handoff, including arm/forearm offsets; camera/head angle input itself is unchanged.
Movement/aiming exit and original poses/graphs/camera controls unchanged. Fresh extraction recommended.
Frame-weight bounds checked at 20/30/60/120/240 FPS, source preservation and archive integrity checked. Native compilation and visual arm movement still require in-game verification.
