SIX-LEVEL CROUCH V4 - RELIABLE HELD SHIFT FAST CROUCH

Close DayZ, keep Steam running, extract ENTIRE ZIP into a new folder, run Launch-Movement-Test.cmd.

While crouched and directional input is held, Shift now EXPLICITLY requests native fast gait3, just as wheel level6 does. Previous Shift path relied on native input handling; v4 makes both paths consistent. This does not change the native fast clips, speed percentages or standing behavior.

Entry from walk/jog/idle still saves60% level3. Entry from achieved full standing sprint saves native6. Holding Shift temporarily makes any crouch level fast; releasing Shift returns to the saved selection (60% after ordinary entry, or6 if entered from full sprint). Changing wheel while Shift held updates saved choice but fast override persists until release. Leaving/reentering crouch resets according to the existing entry rules.

Test repeated Shift+W then crouch without releasing Shift, from both standing walk and jog modes; also diagonal inputs and Ctrl held. Fast crouch must remain active. Test crouch Shift release, wheel changes and standing crouch-exit rules. Existing handoff fix and all animation assets unchanged. Controller mocks include native Shift suppression during crouch to prove explicit override independence; native confirmation still needed.
