MovementLab v85 - native fall animation then timed ragdoll

Male: native death handling/animation allowed initially. At death + 100 milliseconds, enable physics ragdoll. At death + 2000 milliseconds, disable ragdoll and freeze simulation. Respawn remains eight seconds after death observation. The native death animation begins on its normal simulation tick; timing is frame-quantized, not sub-frame exact.

Female: lethal damage remains nonlethal. Start the native unconscious command/fall; at unconscious start + 100 milliseconds, enable ragdoll. At unconscious start + 2000 milliseconds, disable ragdoll and freeze the body. At five seconds, explicitly re-enable simulation, restore health/blood/shock and request upright wake/stand. She remains alive. Repeated hits while down do not extend timers.

Both spawn upright with physics ragdoll off. No per-limb ragdoll switch is exposed by the script API. Timing is polled on mission frames, including while an NPC's simulation is frozen, so recovery and respawn can still run. Checks cover source preservation, timing logic and package integrity; native compilation and animation-to-physics transition/wake behaviour require local DayZ testing. Extract into a fresh folder.
