MovementLab v99 — model-ID writer / animation-ID reader test

Extract into a NEW folder, launch with Launch-Movement-Test.cmd, kill the one
zombie and watch its head for four seconds. Report whether its head visibly moves.
Close DayZ and run Collect-Logs.cmd; send MovementLab-Bone-v99-Logs.zip.

v98 successfully read the animated head using the skeletal lookup, which returned
2090324343. The compiled-model lookup returned 41. Generic matrix writes still
failed with the skeletal identifier. v99 reads the transform/position with the
skeletal identifier and tests the model identifier for the generic writer.
That writer-ID interpretation is a hypothesis, not a verified engine contract.
This exact combination of valid matrix + model ID was not tested in v97/v98.

This is a calibration test, NOT a completed ragdoll. No extra NPC is created.
The temporary head marker, native simulation, one infected, 5-second replacement,
movement, human targets and loadout are unchanged from the preceding test.
Native compilation and the visual result require the local game run.
