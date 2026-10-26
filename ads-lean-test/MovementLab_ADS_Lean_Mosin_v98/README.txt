MovementLab lean test v98 — remove failed elbow overlay

V97 produced flipped arms in native playback. This test starts again from v95: no v96/v97 post-grip elbow capture/restore solver or extra overlay is present. The complete left arm rotation solution is applied only through the existing v32 upper-arm/forearm/wrist nodes, using the same route as the successful lower-hold edits. Original native grip stages remain unchanged.
Right-moving hold stays v95/v94. First-person, body/head/legs, camera and timing unchanged. Ctrl+F8 still compares ON new left pose/lowered holds versus OFF v89 baseline. The target left hold moves both hands/rifle together lower/closer to make the requested left elbow angle reachable, as explained in v97.
Extract into a fresh folder under F:\DayZProjects and launch Launch-Mosin-Lean-Test.cmd. Inspect own-left moving arm shape and grip, then right. If it still differs from the requested pose, send video and Collect-Logs.cmd output.
Local reference math and source isolation passed; native elbow angles remain unverified. V95 is the known working lower-hold rollback.
