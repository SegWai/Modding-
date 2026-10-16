MovementLab v71 - remove synthetic-input feedback and pitch recenter

Built from the v70 rollback (v68 runtime scripts), not v69's persistent world-view implementation. Uploaded v69 logs show the accumulated world target changed by the synthetic handoff turn itself. They also show native HeadingModel output is opposite raw input heading, while rendered world yaw equals the engine heading plus camera local offset. Therefore v69 used both synthetic-contaminated input and an incorrect model-heading sign.

v71 retains v68 yaw compensation without a world-target accumulator or HeadingModel override. The 500ms timeout is removed so compensation cannot hand control back merely because time elapsed. It ends on measured angular completion or native combat ownership. The current full camera pitch is promoted once to normal camera pitch when movement starts, avoiding native free-look pitch recenter. First/third person and third-person prone helpers remain.

Working DayZ 1.30 animation graphs, movement speeds/momentum, stationary head/camera limits, stance icons and MMG/SNAFU loadout are unchanged. Extract to a fresh folder and launch Launch-Movement-Test.cmd. Regression replay of uploaded logs, production yaw-math and package checks pass; native compile and camera playback remain untested here.
