# MovementLab logic names

Agreed terms:

| Name | Meaning |
|---|---|
| Pose smoothing | Blend from the current animation pose to the next while clips keep playing; avoid snapping, freezing or visible restarts. |
| Momentum fade | Enter faster, then smoothly decrease to a target level using a timed smoothstep curve. Current sprint-to-aim and jog2-to-crouch fades take1.5s. |

Suggested shorthand for the other established behaviors:

| Name | Meaning |
|---|---|
| Startup momentum | Build movement gradually from walking to jogging/sprinting. |
| Stopping momentum | Ease through movement states before reaching idle. |
| Reversal inertia | Reduce abrupt opposite-direction changes and repeated zigzagging. |
| Wheel target | Wheel immediately chooses the destination level; controller and pose smoothly catch up. |
| Entry mapping | Choose an initial speed level when entering a different movement mode. |

Pose smoothing describes visible pose continuity. Momentum fade describes the timed speed decrease and its corresponding pose blend. Neither name requires playing the animation backward.
