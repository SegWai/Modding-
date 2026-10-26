FIRST-PERSON ROLL + NATIVE LEFT-WALK CAPTURE v46
The approved v45 body graph and standing-right pose are unchanged.
Native first-person raised view follows Head POSITION but not its rotation.
The new camera hook applies smoothed camera-local roll from the evaluated Head.
ADS/optics uses evaluated weapon-up roll after the native sight-camera update.
Camera position, aim direction, FOV, native ADS selection and body poses remain.
No forced ADS, default animation replacement, camera heading change or teleport.
Native camera compilation/visual correctness need Windows DayZ testing.

1. Extract into a new folder and launch Launch-Mosin-Lean-Test.cmd.
2. Test first-person Q/E with the gun raised, then actual ADS/optics.
   F7 compares custom/native. F9 logs applied camera roll and starts clip capture.
3. The requested character-LEFT walking/leaning clip records automatically on
   launch. Let the NPC patrol at walk pace; wait for "Left walk clip captured".
   F9 logs camera/pose status and starts a fresh clip capture if needed.
4. Close DayZ. Run Build-Left-Walk-Blender.cmd to generate the .blend locally,
   OR run Collect-Logs.cmd and send the ZIP so the clip can be built for you.
The collector samples 36 consecutive frames at nominal 24 Hz in one leftward
walking/aiming lean pass. It rejects direction changes, non-walk pace and gaps.
Every sample logs all 114 bone transforms, weapon transform and actual game time.
Existing v43/v44 captures contain sparse stills, not a continuous walking clip;
no pretend intermediate animation is supplied from those stills.

Blender importer: uses included weighted template, imports one captured pose per
Blender frame, with constant interpolation and an actual-time marker per frame.
Raw native transforms preserved in a text block and adjacent JSON. Mesh bone
axes differ from native, so rotations are landmark-fitted with inherited twist.
All joint origins are verified against each captured sample. The rifle is a
schematic guide at the measured transform, not the original weapon mesh.
Save edits to a new .blend and send back the file with the desired frame number.
