Standing Scroll Mode Links v1 — separate test; previous versions preserved.
Close DayZ, extract entire ZIP, run Launch-Movement-Test.cmd.
Walking levels:1 ~85%,2 100%,3 120%,4 121% boundary -> native jogging.
Jogging levels:1 99% boundary -> walking120%,2 native100%,3 130% retained.
Walking121% and jogging99% are immediate mode triggers, not separate clips.
One notch above walk120 selects jogging100, not jogging130.
One notch below jogging100 selects walking120, not walking100.
Jogging130 scrolls down to jogging100, then walking120 on another notch.
Walking default remains~85% and walking selection resets on crouch exit.
Existing Ctrl walk/jog toggle, Shift sprint, acceleration/braking timers,
direction rules and independent crouch wheel retained.
Wheel boundaries apply during standing walk/jog, including at rest; Shift,
menus, prone, crouch and vanilla comparison retain prior input scope.
Existing ~85% clips are26FPS=86.67%; jogging130% clips39FPS.
No new screen messages or F8 toggle. Logs record transitions.
Native DayZ animation/velocity validation pending. If incorrect, close DayZ,
run Collect-Logs.cmd and attach MovementLab-Linked-Wheel-v1-Logs.zip.
