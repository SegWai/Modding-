MovementLab v13 - Native reversal pose experiment (v11 baseline)

Close DayZ, keep Steam running, extract this entire ZIP into a separate folder,
and open Launch-Movement-Test.cmd. No Addon Builder or animation import needed.

Jog sideways A then D; test D then A. Also test W then S and S then W.
Wait until actually jogging before reversing. The hold lasts 0.32 seconds.
F8 toggles ONLY this native-pose reversal experiment; OFF retains v11 behavior.
F7 switches the original heavier movement vs vanilla filters.
Test on flat ground, standing, empty hands. Manual Ctrl walking bypasses it.

The experiment requests CMD_SlidingPose and holds the OLD-direction run pose.
Horizontal animation translation is zeroed inside the temporary script command.
Then native movement resumes toward the currently held keys; releasing leaves idle.
V11 startup/stopping durations and its stable installation are unchanged.

Observe: Is the foot-out bracing pose retained? Does the body remain in place?
Does movement resume on the correct side without a forward walking step?
The native graph may blend out despite repeated commands: this is a test,
not confirmed in-game behavior. No native Enforce compiler runs in the cloud.

Logs: Profiles/MovementLogic (script log). Search [MovementLab v13].
START gives angle/hold time. END gives elapsed time, horizontal displacement,
command request count and cancellation status. Send a script error screenshot
if DayZ fails to launch, or a video if the pose/transition is wrong.
