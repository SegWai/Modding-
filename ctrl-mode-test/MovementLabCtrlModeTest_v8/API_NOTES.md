# v8 permanent responsive body rotation

Based on v7. Removed m_MovementLabResponsiveTurn, its KC_F8 handler and A/B
status text. Custom-profile SetTurnSpanModifier is permanently 1.6, exactly
v7 with its preferred responsive setting enabled. SetDirectionFilterModifier
remains 2.5; sprint and run/sprint modifiers retain their existing values.
F7 retains its separate native whole-profile comparison.

World source and mission cancel/start/brake/finish methods are byte-identical
to v7. All four crouch rules and standing Ctrl/Shift behavior are preserved.
No animation frame, gait curve, timing or camera changes are added.

check_fixed_turn_v8.py executes actual translated old/new filter methods,
comparing all five setter outputs against v7 responsive mode across custom/
vanilla, braking and stamina states. F8 must not change output or cancel
movement state. Source equivalence checks preserve tested v7 movement logic.
Native Enforce/animation/physics validation requires local DayZ.
