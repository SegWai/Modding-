# v107 command-context correction

v106 logs: all three captured poses failed readback (position errors 0.81–1.48 m; basis errors 1.88–2.00). Each hit the 1.5 second timeout and resumed native death. No ragdoll activation occurred.

v107 fixes a documented API-context violation: the bridge queues graph values, and only the custom corpse CommandHandler calls AnimSetFloat. It resubmits the controls each command tick and records a revision acknowledgement. Baseline capture and verification each wait an additional native command tick after submission. The maximum handoff wait is reduced to 350 ms. Failed matching still restores native death; this is not claimed to be a proven pose-continuity fix.

The 91-bone graph, pose-error limits and momentum calculation are unchanged. Detailed core-joint target/baseline/actual diagnostics identify remaining axis, propagation or graph-evaluation errors. Other player movement, camera, smoothing, equipment and fixtures are unchanged.

Extract this folder separately and run Launch-Movement-Test.cmd. Test standing with arms raised, running, attacking and crawling deaths. Run Collect-Logs.cmd after testing. Native compilation/gameplay cannot be run in the cloud.
