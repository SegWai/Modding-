v61 reverses v60 stationary correction feedback
User reported v60 moved the torso farther right. The measured shoulder yaw is now subtracted from the current correction instead of added. Correction bounds, smoothing, Spine3 axis, Neck counter-rotation, stationary/non-aiming eligibility and movement exit behavior are otherwise unchanged.
Normal movement lean and arm swing remain; camera, head-look blending, speed/momentum and loadout unchanged.
Source and ZIP checks passed. Native direction and actual shoulder convergence require local verification; send logs if the torso still fails to settle square.
