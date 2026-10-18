MovementLab v98 — infected render-bone calibration

1. Close DayZ and extract the complete ZIP into a NEW folder.
2. Run Launch-Movement-Test.cmd with Steam running.
3. Kill the one zombie, then watch its HEAD closely for 4 seconds.
4. Note whether the head visibly moves/stretches up and down after death.
5. Close DayZ, run Collect-Logs.cmd, and send MovementLab-Bone-v98-Logs.zip.
   Tell us whether you saw the head move; readback alone cannot prove rendering.

This is a deliberately visible bone-write test, NOT a finished ragdoll.
No extra human/proxy is created. Living infected AI and 5-second confirmed-death
replacement remain native. The head write is applied in POSTFRAME with simulation
left enabled, so it tests a different timing path from the failed v94 copying.
The test uses a fixed cached baseline and bounded 0..0.35 model-unit offset for
3 seconds. It does not accumulate translation, add impulses or change health.
Human fixtures, movement, loadout, grenades and Gunter remain unchanged.

v96 returned zero bone physics bodies even for the human with ragdoll=true.
That inspection API cannot distinguish the two controllers. It does not prove
that infected ragdoll is impossible. A usable render-bone write path is needed
before attempting a custom articulated-body simulation for the infected.
Native compilation/rendering must be tested in DayZ; cloud packaging checks
cannot verify the visual result. If there is an error, collect logs anyway.

v98 corrects the lookup to inherited DayZCreature.GetBoneIndexByName. It logs the
proxy index separately and rejects a zero basis. If matrix reading is unavailable
but a valid skeletal position exists, the temporary head marker uses an identity
basis at that position. If neither can be read, the test aborts without writing.
Please watch the zombie head for four seconds after killing it and send the logs.
