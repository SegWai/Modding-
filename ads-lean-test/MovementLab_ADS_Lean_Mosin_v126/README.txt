V126: LEFT walking targets X=+2cm toward character own right, Y=+0.8140797cm, Z=+15cm from v117. The final support-grip pass now uses RightHand as weaponrotator and enables its aim construction, matching the hand-anchored configuration of the existing post-pose support solver. Primary/right-arm solve remains off; it does not publish a new weapon offset. The preceding rifle-position publisher and its roll target remain in place. This is a native grip-alignment test, not a separate hand-Z slider. Actual foregrip contact and weapon orientation need in-game verification. Right walking X=+5cm, all controls, recorder and camera retained.

V126: LEFT walking target from v117 X=2.000000cm, Y=0.814080cm, Z=15.000000cm. Right hold, final support-grip ordering, all scripts/recorder/controls/camera retained from v125. Native visible position and grip require verification.

V125: left-walk support-hand alignment test. Restore the v123 weapon publisher (support solve off), publish the adjusted weapon pose first, then run a separate support-only native IK node using the current weapon foregrip target. The final support node has no weapon-offset publication and no primary/right-arm or aim solve. This preserves the existing gun-position controls rather than changing whole-hold Z. LEFT targets X=0/Y=+0.8140797/Z=+15cm; RIGHT X=+5cm and prior Y/Z retained. Native hand alignment/skin deformation/weapon placement still need verification; source checks cannot establish native node evaluation semantics. All controls, recorder, camera and scope retained.

V125: enable native secondary/support-hand IK in the final left-walk weapon publisher, AFTER the custom hold displacement. The solver uses the current weapon's native LeftHandIKTarget each evaluated frame. Primary/right-hand solve and aim remain disabled in this late layer so it does not intentionally pull the shifted weapon back to the default hold. Zero native blend delay. Position targets stay unchanged: LEFT X=0/Y=+0.8140797/Z=+15cm from v117; RIGHT X=+5cm with prior Y/Z. Right-walk path, first-person, crouch, recorder and controls are unchanged. The left elbow may bend differently as the support hand returns to the foregrip. Native grip/weapon placement still needs verification.

V125: RIGHT walking raised lean X=+5cm toward character own right, relative to its original v117 right hold; Y/Z unchanged. LEFT walking targets unchanged from v122: X=0, Y=+0.8140797cm, Z=+15cm relative v117 left reference. Both palms follow; shoulder roots and reference segment lengths/orientations preserved. Same third-person standing shouldered-gun scope, Ctrl+F8, recorder and AJ/CF. Native visible placement unverified.

V125 combined targets relative to v117: X=0cm, Y=+0.8140797cm, Z=+15cm (restored from v119). Compared with v119, only X changes from -3.4483846cm to zero. Scope, recorder and controls retained. Native visible placement unverified.

V125: add 10cm forward to v119. Targets relative to v117: X=-3.4483846cm, Y=+0.8140797cm, Z=+25cm. Other settings and scope retained. Native visible placement unverified.

V125 manual left-walking hold target relative to v117: X=-3.4483846cm, Y=+0.8140797cm, Z=+15cm. Only Z changes from v118 (+9.4701338cm), adding 5.5298662cm forward. Both hand targets move together; shoulder roots, palm orientations and native reference limb lengths remain fixed. Same shared NPC/player scope, recorder, AJ/CF and Ctrl+F8. Native visible placement unverified.

V125: match the working right-walk shoulder-to-rifle contact using actual v117 native captures, rather than the earlier authoring references. Remove the ineffective shoulder translation nodes. Apply eighteen late arm/forearm/wrist rotations while keeping shoulder roots fixed, grip orientation and reference segment lengths preserved. The measured stock proxy correction is approximately 3.45cm character-left, 0.81cm up, 9.47cm forward, applied equally to both hands. This targets the first reference image's shoulder contact; it is not an additional fixed 5cm shift. The proxy is calibrated to the RightShoulder bone in the accepted hold, not to a measured stock mesh vertex. Activation waits for the existing one-shot elbow calibration. Same own-left standing raised walking scope; Ctrl+F8, recorder, female NPC, AJ/CF, first-person and right-walk paths retained. Native visual/contact outcome still needs testing.

V125 — female movement recorder and quiet controls; weapon 5cm forward

The male NPC keeps his current patrol and custom poses. A second NPC, SurvivorF_Eva in a blue hoodie, spawns 10 metres to HIS own right (relative to his initial facing direction). Both use the same custom player/NPC graph. The female stands idle until playback starts. The current left-walking weapon hold has no sideways offset: both hands/weapon target move 5cm character-forward (+model Z) from the original reference. Left elbow target 20 degrees and right elbow 45 degrees outward from straight down are retained. Native visible angles/offsets remain reach-constrained and require testing.

CONTROLS
- Ctrl+F8: the only retained old test toggle; arm comparison ON/OFF.
- Tap L: start recording; tap L again: stop recording.
- Colon (:): replay the recorded sequence on the woman in a loop.
- Tap L during playback: stop the loop and hold her last pose; it does not start a new recording on that same tap.
- Hold L for 0.75 seconds: stop/clear the recording and return the woman to her starting spot. Release, then tap L to record again.

The colon key is accepted as semicolon/colon on US layouts, Shift+period on Portuguese layouts, or the native colon key code. Other added F5/F6/F7/F8/F9/F10 and Ctrl+F9 comparisons are removed. All added in-game notifications and timed distance-calibration prompts are removed; recorder state is written to logs instead. Controls are ignored while a game menu/text-entry menu is open. A short L tap is committed on release so a long hold can clear without accidentally starting another recording.

REPLAY
Recording samples actual movement at up to 20Hz, including turning, walk/run/sprint, standing/crouching/prone, lean, weapon raise and aim direction. Playback interpolates those samples and uses native locomotion. Relative paths rotate into the woman's starting facing direction. Every loop returns to her starting spot; paths ending elsewhere will visibly return at the loop boundary. Playback corrects positional drift over 25cm. Maximum 6000 samples (about 5 minutes); recordings are in memory for this game session.

At playback start she receives the weapon held when recording began, with its direct attachments and loaded ammunition. Weapon switching, reload/firing events, emotes, jumps/vaults, inventory and other interactions are not recorded. This is movement/pose replay, not full gameplay replay. Terrain/collisions and female proportions can affect native motion. Both NPCs retain ragdoll/one-second respawn handling; if she dies, playback stops and the recording remains available after respawn.

DEPENDENCIES / LAUNCH
Install/download Community Framework (1559212036) and AJs Weapons (3571685323) through Steam. Launcher loads CF, AJ, workspace, then logic. No Workshop files are redistributed. Extract the full ZIP and run Launch-Mosin-Lean-Test.cmd. Default game: D:\SteamLibrary\steamapps\common\DayZ; project root F:\DayZProjects. Run Collect-Logs.cmd after testing if replay fails. The ZIP contains runtime essentials only.

Local source, math and package checks do not establish native compilation or playback correctness. The female replay controller has not been run in Windows DayZ here. Previous versions remain separate rollback ZIPs.
