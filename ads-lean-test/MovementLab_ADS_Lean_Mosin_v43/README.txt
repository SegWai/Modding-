POSE CAPTURE v43 — approved v41 animation remains unchanged.
Fix: native Human bone identifiers can be NEGATIVE. v42 incorrectly omitted
56 of the 114 named bones, including the right hand and both forearms.
This version queries every named bone regardless of its identifier sign.
1. Launch-Mosin-Lean-Test.cmd.
2. Let the NPC patrol normally. Press F9 ONCE.
3. Wait for "Pose capture complete" (usually within 10 seconds).
4. Close DayZ, run Collect-Logs.cmd, and send the ZIP.
Automatic capture waits for full moving lean and 0.4 seconds of stable direction.
It records each direction once, with a 30-second timeout and completion message.
All animation graph/PBO data and player/NPC pose control remain unchanged.
Native Windows compilation and capture validation still require running DayZ.
