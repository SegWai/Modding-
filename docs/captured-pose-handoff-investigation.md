# Exact captured-pose handoff: requirement and groundwork

## Requirement clarified by the user

The visible infected must enter physics from the last evaluated animation pose at the alive-to-dead transition: raised elbows with low hands, spotting/reaction poses, attack frames, walking/start-to-jog frames, running and crawling. Preparing a generic standing, fists-raised or prone Human animation is not the requested result. Global travel momentum works in v102 and should be retained. Approximate stance seeding in v103 is not a solution to exact-pose continuity.

The user's follow-up crawling test stayed near the ground but showed a split-second standing body and then ordinary death behavior, with no visible ragdoll. Record this as a failed crawling handoff. The earlier uploaded v103 log contained13 non-crawling deaths and cannot diagnose this later crawling event. Its fresh logs are needed to distinguish detection failure, low-pose timeout/fallback, or transient visibility during replacement initialization. A standing flash alone does not identify the actor or event responsible.

## What the inspected APIs/assets support

The inherited skeletal lookup and GetBoneTransformMS read valid infected transforms (verified v98+). Generic SetBoneMatrix/GetBoneMatrix reject both tried identifiers; SetBoneGlobal did not visibly change the model. Repeating those writers is not a supported pose-transfer strategy.

The supplied native AGF files contain AnimSrcNodeProcTransform with Model/Local axes, Rotate/Translate operations and expression-driven amounts. Existing HumanAnimInterface binding and actor AnimSetFloat provide a possible graph-controlled path. This is evidence of graph features, not proof of an arbitrary full-pose handoff. Native fixed-axis rotation order, pivot behavior, propagation to descendants, matrix conventions, evaluation timing and physics snapshot timing still require verification. No new gameplay package using this route has been installed/published.

## Completed offline work

`tools/captured_pose_bridge.py` computes parent-before-child corrections from reference and desired rigid model-space transforms. It propagates the desired parent before solving a child's residual so parent rotation/translation is not applied twice. It includes a theoretical reconstruction and generator for per-bone rotation/translation graph controls and nodes. The fragment is explicitly unverified and not a complete workspace; it does not activate or seed physics.

The explicit mathematical convention is column-vector4x4 transforms, X thenY thenZ rotations in fixed model axes about each bone's own pivot, followed by model translations. Native vector[4] basis-row data must be converted at the boundary. Native graph semantics must match or the converter/order must be adjusted; mathematical reconstruction cannot certify that.

Six tests cover50 deterministic arbitrary branched poses, parent corrections, prone/root translation, gimbal limits, identity poses, invalid transforms/hierarchies and graph-fragment structure. The actual supplied XOB rest transforms have91 common nodes; correction/reconstruction has maximum matrix error1.67e-14 under the offline convention. That verifies the math for these inputs, not a dying animation, native skeletal writes or rendered continuity. A full91-node graph would currently require546 controls/procedural nodes; performance and native limits are unverified and must be assessed before integration.

## Remaining native implementation and checks

1. Capture named infected transforms at death, plus its previous evaluated pose if limb velocity is to be reconstructed. Do not classify the full pose from hand height or gait alone.
2. Add a dedicated replacement-only graph branch, with an inactive-by-default per-instance gate. Player/other NPC graph output must remain unchanged.
3. Bind all required controls and demonstrate a known graph-driven joint correction in the actual runtime. Verify axes, units, pivots and parent propagation before using the generated full chain.
4. Compare replacement transforms with the captured target after native graph evaluation. A pose-error threshold, rather than a stance-height heuristic, should guard the ragdoll handoff.
5. Test visibility and source death-animation ownership during initialization. Prevent any standing replacement frame for a crawling death; retain rollback if the captured pose cannot be established.
6. Enable physics only after the measured pose matches, retain verified global momentum, and validate arm/leg continuity during actual idle/attack/run/crawl deaths. Native pose evaluation/death processing may still replace the seeded pose; this remains unresolved.

No exact-frame preservation or crawling success is claimed. The existing v103 remains an approximate experimental build, and the latest reported crawler result is a failure requiring its runtime trace.
