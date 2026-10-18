MovementLab v96 — native physics inspection test

1. Close DayZ. Extract the complete ZIP into a NEW folder.
2. Run Launch-Movement-Test.cmd as usual (Steam running).
3. Shoot the jogging male NPC until he dies. Then kill the ONE zombie, 20m ahead.
4. Wait at least 4 seconds after each death. Close DayZ.
5. Run Collect-Logs.cmd and send MovementLab-Physics-v96-Logs.zip.

No debugger or Workbench setup is needed. The snapshots run automatically.
This is a diagnostic build, not a confirmed zombie ragdoll fix.

Based on v93: native living infected AI, confirmed-death replacement after five
seconds; existing human ragdoll, loadout, gear, locomotion, grenade and car setup.
The failed v94/v95 hidden-human/model-swap proxy is absent. Diagnostics only read
physics state. They do not force animation, simulation or body visibility.

If a compile error or crash occurs, close the game and run Collect-Logs.cmd
anyway. The last stage marker helps identify an unsupported native operation.
The native DayZ compiler/runtime is not available in the cloud, so the test is
not claimed to have been compiled or played locally here.
