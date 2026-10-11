SIX-LEVEL CROUCH V2 - 87% TO NATIVE HANDOFF TEST

Close DayZ, keep Steam running, extract ENTIRE ZIP into a new folder, run Launch-Movement-Test.cmd.

Same six levels:30%,approximately47%,60%,approximately73%,approximately87%,native fast crouch. Same original controller, timers, standing/strafe rules and clip FPS. No hidden stage/F8/momentum experiment.

One gameplay change: graph levels5 and6 now select the SAME L5 crouch source group. At5 gait1 uses26FPS walk. At6 gait3 uses the original native fast-crouch run clips already mapped in that group. Thus the5->6 switch keeps its current walk source active while the native gait filter catches up; it no longer immediately falls back to the9FPS walk clip in the separate original Cro group. Fast endpoint clips remain original native assets. The old Group6 remains declared but is not selected.

This targets the dip visible in the uploaded3.2-second excerpt, where the leg pose lingers before movement resumes. Native measured gait timing was not available in logs for that recording; this is a test of the identified code-path hypothesis, not a confirmed visual fix.

Test forward crouch at5, scroll up once to6 without releasing movement, then scroll down to5. Also test Shift from5 and lower levels, plus diagonal/backward movement. Previous six-level ZIP and stable v1 unchanged. Controller/schema/package checks passed locally; native DayZ test pending.
