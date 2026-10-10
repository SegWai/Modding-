# V13 native reversal pose experiment

Isolated copy of stable v11. Does not contain v12 braking/startup alterations.
Existing v11 archive/source remain byte-for-byte unchanged.

Uploaded player_main.asi maps Locomotion.Erc.RunSlidingPose to
DZ/anims/anm/player/layered/stop/p_erc_run_stop_poses.anm. Locomotion.agr
SlidePoseRun samples (MovementDirection+180)/360. The SlidingPose state
is entered with CMD_SlidingPose; its 12 ordinary movement/idle exits are
eligible after GetLowerTime()>0.18. Their blend spans are 0.3 seconds.

The existing graph is not replaced. A temporary HumanCommandScript follows
the official Test_ScriptCmdSwim architecture: bind command/variables,
PreAnim_CallCommand, PreAnim_SetFloat, PrePhys_SetTranslation and return
false from PostPhysUpdate to finish. Native default finished-command handling
returns to HumanCommandMove. ModCommandHandlerInside handles only this
owned script command; death/falling/finished-command lifecycle remains native.

For 0.32 requested seconds: animation gait=2, direction=old movement angle,
CMD_SlidingPose is requested each animation tick, horizontal translation is
zeroed, vertical animation translation is preserved, rotation is locked.
Gravity is not disabled and there is no world position teleport. Repeating
the command may re-enter/retain/reset the pose or fail to prevent blending;
these outcomes require local engine testing. The graph's normal timer and
native command parameter semantics are not overridden by this package.

Trigger compares raw input direction vectors, including most-opposite diagonals,
only after native jogging gait>=1.75 and outside walking startup/manual walk.
New opposite key presses detect overlapping old/new held buttons. Inputs during
hold cannot restart its timer; current keys decide motion after finish.
F8 disables only the experiment; F7/mission exit/UI/pause/death/raised hands,
items/falling/large simulation steps guard the command. Standing unarmed,
offline local player only. Camera-driven reversals are not intercepted.

Stationary pose retention, collision/gravity, animation handoff, native
compilation, command retrigger semantics and online replication are unverified.
END logs report actual position delta to help distinguish a pose from a true
horizontal movement pause. API inspection and packaging do not prove gameplay.

Actual command methods were mechanically translated to C++ and tested in a
mock SDK at 30/60/144 FPS: duration, constant pose direction/gait, X/Z suppression,
vertical preservation, cancellation and invalid binding passed. Native graph
transitions and input/native physics ordering are not modeled. The repository
harness is tools/check_movement_logic_experiment_v13.py.
