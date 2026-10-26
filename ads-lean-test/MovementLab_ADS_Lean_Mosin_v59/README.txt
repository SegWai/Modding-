FIRST-PERSON RIFLE ALIGNMENT / SUPPORT GRIP v59
v58 loaded successfully in the supplied logs, but its camera alignment was not
instrumented. It corrected eye position without rifle-relative view orientation.
v59 preserves both neutral eye spacing and neutral rifle-to-view orientation
while leaning. Only the raised first-person camera changes; native ADS/optics
cameras remain as before. No input, ammo, recoil or weapon transform writes added.
Vertical support-hand IK no longer depends on the native ArmIK support bit.
Its output still blends only while custom leaning and aiming vertically. Primary
hand and weapon aim/roll settings remain untouched; level third-person pose exact.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
Hold the gun raised WITHOUT leaning for 2 seconds first (record neutral view).
Then test LEFT and RIGHT, looking level, up and down. Test third person too.
If it persists, close DayZ and send Collect-Logs.cmd output: new MLCAM59 readback
shows reference status, camera correction and camera/rifle direction.
F7 comparison, F9 measurements, F10 NPC pause. Runtime files only.
Source/matrix/PBO checks passed; this is a test build, not native-verified fix.
