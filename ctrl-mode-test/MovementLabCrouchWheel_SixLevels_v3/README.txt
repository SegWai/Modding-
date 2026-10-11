SIX-LEVEL CROUCH V3 - ENTRY DEFAULTS

Close DayZ, keep Steam running, extract entire ZIP to NEW folder, run Launch-Movement-Test.cmd.

Every new crouch entry from walking, jogging or idle resets to level3 (60%), regardless of the previously selected crouch speed. Entering from achieved full standing sprint selects level6 (native fast crouch). Full sprint detection uses last upright native movement gait>=2.90 of3; merely tapping Shift during walk/jog startup does not select6 as the saved entry level. Holding Shift in crouch still temporarily requests native fast gait under the existing rules.

Scroll wheel selects30%,47%,60%,73%,87%,native while staying crouched. Leave crouch and enter again: default60%, except full standing sprint. Native sprint entry6 remains selected after Shift release until scrolled or crouch exited. Original crouch-exit standing jog/walk rules retained. Existing87%-native source handoff correction retained. No hidden stage or F8 experiment. Standing timers/strafe unchanged.

Test walk->crouch, jog->crouch, idle->crouch (all60%); full sprint->crouch (native). Select each different crouch speed, leave then re-enter (60%); check fast crouch exiting directly into jog then crouch does not count as standing sprint. Native compilation/visual confirmation pending; translated controller/schema/package checks passed locally. Previous packages unchanged.
