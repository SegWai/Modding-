# v9 Ctrl jog-to-walk momentum at the existing deadline

Based on v8. The generic target-walk brake when not using the sprint-stop
curve now uses smoothstep t*t*(3-2*t) in place of ease-out 2*t-t*t. Duration,
start/end gait and ownership are unchanged. It preserves more momentum early
and has zero slope at both endpoints. No held-frame interval, new timer,
extra animation cycle or walking tail is added. Gait is not measured m/s.

Only generic Ctrl jog-to-walk is changed. The zero-target stopping envelope,
sprint-to-walk stop-curve reuse, sprint-to-jog return and native direction
ownership retain their existing logic. World crouch/start/mode source is
unchanged from v8; permanent responsive body heading and F8 removal remain.

check_ctrl_modes_v9.py executes actual translated mission/World methods. New
versus v8 comparisons span 30/60/144 FPS, eight direction masks and achieved
gaits 1.8/2/2.05, verifying monotonic speed, higher early requested gait and
identical duration/completion tick. Existing standing, back-diagonal, full-stop,
sprint-to-walk and four-crouch-rule regressions pass. Filter code matches v8.
Native Enforce/animation/physical velocity testing remains local in DayZ.
