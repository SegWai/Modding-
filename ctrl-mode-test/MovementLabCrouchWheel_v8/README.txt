CROUCH WHEEL V8 - ANIMATION TABLE REPAIR TEST

Close DayZ, keep Steam running, extract the ENTIRE ZIP into a NEW folder and run Launch-Movement-Test.cmd. No Addon Builder required. Original DZ files remain read-only.

V7 RPT showed1206 missing-source-ID errors (323unique) and Invalid columnLocomotion errors. V8 restores the native Locomotion template column exactly (10 original groups,58slots). Extra retimed groups live in a new separate column with matching cloned crouch source nodes. Hidden mappings are corrected to be INSIDE the animation profile's $animations block; v5-v7 mistakenly wrote them outside. Template links use the explicit patched path. New custom groups are sorted.

Level5 now directly selects the original native Cro movement subtree; it does not depend on the added speed column.

FIRST: leave F8 OFF, crouch and scroll up through levels1..5. Check level5 is native fast crouch, not a frozen ladder animation. Also test normal standing movement and Shift crouch.

THEN: F8 ON enables the downward-only hidden90 bridge; level5 to4 passes through a brief automatic90 stage. Still only5 selectable levels. Upward scroll never triggers it; Shift/stop/stance exit/F8 OFF cancel it.27FPS is90% slow-crouch clip timing, not measured90% of native fast velocity. Standing/strafe rules unchanged.

Local controller/schema checks passed. Native table loading and visual result require this DayZ test. If still wrong, close DayZ, run Collect-Logs.cmd, attach MovementLab-v8-Logs.zip. Existing older archives unchanged. Included KnownWorkingV1 is a legacy control only; its extended template layout is superseded by this repair.
