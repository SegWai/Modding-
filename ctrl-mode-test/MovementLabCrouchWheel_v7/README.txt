CROUCH WHEEL V7 - SINGLE SELECTOR AND EXACT V1 CONTROL

Close DayZ, keep Steam running, extract the entire ZIP into a NEW folder.

FIRST: run Launch-Known-Working-v1.cmd. This uses an isolated, byte-for-byte copy of original working v1 source/assets/launcher/PBO. Test crouch level5. Close DayZ afterward.

SECOND: run Launch-Movement-Test.cmd (v7). F8 OFF is default. Test level5 again. F8 ON enables the downward hidden90 test.

V7 removes all extra nested/timed wheel wrappers. There is one original-style wheel BlendN selector, adding a hidden input at4.5. Original fourteen group indices are preserved; hidden group appended at end. F8 OFF feeds only the original five integer levels and original v1 crouch gait decisions. F8 ON: level5 scroll DOWN goes through4.5 automatically, then4; .10s entry, .10s hold, .10s exit. Further downward scroll queues lower target. Scroll UP/Shift/stop/stance exit/F8 OFF cancels. H90 is27FPS slow-crouch clip timing, not measured90% of native fast velocity.

Standing/strafe controller unchanged. Native result unverified here. If v7 still freezes but the exact v1 control works, close DayZ and run Collect-Logs.cmd; send MovementLab-v7-Logs.zip. If v1 control also freezes, report that too: it points beyond the hidden-stage changes, and logs are needed before another animation change.
