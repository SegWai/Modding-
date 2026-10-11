Crouch Descent v1 — separate test from preserved corrected scroll v2.
Test crouch level5 ~87 ->6 native fast ->5 ~87 while moving continuously.
Only fast-to87 descent changes: request falls through existing fast/walk blend
range over0.28s, then reaches normal slow gait over0.10s. No hold/freeze.
Animation graphs/foot markers/clips untouched. Ascending behavior unchanged.
Shift release to savedlevel5 also uses descent. Shift press interrupts intofast.
Further scroll tolevels1..4, stopping input, stance exit or invalid context cancels.
Timer advances once per command frame, never twice through mission callback.
Native phase preservation not proven; this tests downward timing first.
Close DayZ, extract ZIP, launch as before; Collect-Logs.cmd if ineffective.
