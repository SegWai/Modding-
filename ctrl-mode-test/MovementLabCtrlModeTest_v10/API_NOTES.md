# v10: later walk entry after Ctrl with the existing transition budget

Based on v9. Generic target-walk mode braking (not the sprint-stop envelope)
remaps normalized time to u=clamp((t-0.2857143)/0.7142857,0,1), then uses
smoothstep u*u*(3-2*u). At achieved full jogging, this keeps moving jog gait
for 0.12s before the 0.30s walk blend. The total remains 0.42s. The shorter
backward/partial-gait budgets retain their original lengths and proportional
lead/blend. This requests continuous native jogging, not a frozen frame.

Only this Ctrl jog-to-walk curve changes. World crouch/start/mode logic and
filter code match v9. Permanent responsive turning, F8 removal, sprint returns,
released-input stopping curves and four crouch rules are retained. No direct
position, m/s velocity, clip timing or frame edits are added.

Actual translated methods at 30/60/144 FPS compare against v9 over eight input
masks and achieved gaits 1.8/2/2.05. Initial request equals starting gait;
subsequent easing is monotonic, remains above v9's request and completes on
the same tick/deadline. Existing both-callback-order movement/crouch tests
and v11 stop/sprint-to-walk comparisons pass. Native animation/physics behavior
and Enforce compilation require local DayZ; the gait tests do not measure them.
