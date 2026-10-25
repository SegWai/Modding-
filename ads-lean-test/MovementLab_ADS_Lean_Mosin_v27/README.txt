Lean range v27 — graph resource loading repair test

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Existing range/equipment/ammo/respawn retained.

Your v26 logs contain an animation-expression compilation failure for the shoulder offset and an invalid-root-graph error, despite successful script bindings/F5 messages. V27 gives the modified locomotion fragment its own resource path/GUID and refreshes the custom control-template identity. It no longer overrides the shared vanilla locomotion fragment.

All v26 pose values and body movement are unchanged, including the35cm anatomical-right shoulder/arm offset BEFORE native weapon IK. Same graph for player and NPC. Native compilation/appearance still require a game test.

F5 toggles the moving offset ON/OFF; starts ON. Leave it ON for a complete left/right pass, press F5 once, then let him complete another pass. The test automatically logs chest, both hands and rifle positions at stable full lean in each direction. No need to time F9. F10 pauses NPC but removes moving-only offset. F6 head comparison; F7 native/custom; F8 third-person inspection; F9 manual diagnostics.

Close DayZ and run Collect-Logs.cmd. Send the v27 ZIP with the result, especially if there is still no change. Script binding success does not establish that the animation graph compiled.
