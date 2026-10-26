FIRST-PERSON FRAMING / VERTICAL GRIP v58
Raised first-person camera preserves the neutral eye-to-rifle spacing when leaning
left/right, and removes the added raised-camera roll. This fixes position framing,
not just roll. Native view direction, FOV and firing/input controls stay unchanged.
ADS/optics camera behaviour remains unchanged.
A final support-arm-only IK pass tracks the final rifle while aiming up/down on
either side. No primary/right-hand, gun-aim or gun-roll solve is enabled there.
Level-aim third-person pose remains exact; vertical aim may move the support arm
to keep contact. Earlier smooth transitions and head travel targets remain.

Extract into a NEW folder under F:\DayZProjects. Launch-Mosin-Lean-Test.cmd.
FIRST hold gun raised without leaning for 2 seconds to record neutral framing.
Then Q/E in first person, and aim up/down. Test the same in third person: the
rifle and level pose should match the previous version, and the support hand
should stay on the rifle at vertical angles. Also test ADS, walking and crouch.
F7 native/custom. F9 diagnostics. F10 NPC pause. Close DayZ, Collect-Logs.cmd
if needed. Runtime essentials only. Native Windows playback still needs testing.
