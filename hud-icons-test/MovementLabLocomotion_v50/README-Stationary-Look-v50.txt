v50 hard camera limit
Stationary non-aiming camera yaw is clamped to +/-145 degrees relative to the body after mouse sampling and after reading the current body heading. Large mouse deltas cannot queue hidden rotation beyond the cap. Existing full-body turn remains enabled at the boundary (0.001-degree floating-point tolerance), and the cap follows the body as it turns. Visible head remains +/-90 degrees. No other gameplay/graph/loadout changes.
Boundary/overshoot math and ZIP integrity checked; native DayZ compilation and runtime testing remain pending.
