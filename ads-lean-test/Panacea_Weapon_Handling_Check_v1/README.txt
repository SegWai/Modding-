Panacea Weapon Handling Check v1

This is a separate diagnostic session, not an animation rollback. The v106 custom animation package is unchanged.

1. Close DayZ. Extract this entire ZIP. Run Launch-Handling-Check.cmd.
2. Test raising, ADS and firing with 1 (vanilla AK74), then switching to 2 (Panacea SCAR-H) and 3 (Panacea AWM).
3. Close the game and run Collect-Logs.cmd. Send that ZIP and say which weapons worked.

Only The Panacea Weapons (Workshop 2389010221) plus a tiny DayZDiag inventory-debug compatibility helper load. There are NO custom animation workspaces, PlayerBase patches, camera corrections, weapon-profile registrations or ammo refill loops in this test. No attachments are added, apart from each weapon's loaded magazine. If a stored rifle cannot fit it is placed beside you and logged.

If the Panacea guns still fail here while AK74 works, the fault also exists without our animation code. If they work here, the custom integration needs further isolation. If AK74 also fails, the logs will help identify a broader offline/game/mod issue. None of these outcomes is asserted in advance.

The launcher locates the installed Panacea Workshop folder automatically or asks for its path. Workshop files are not redistributed. Default game path: D:\SteamLibrary\steamapps\common\DayZ. The current custom animation files are not modified. Diagnostics are sampled once a second for at most two minutes. Logs stay in this test folder under Profiles\PanaceaHandling.
