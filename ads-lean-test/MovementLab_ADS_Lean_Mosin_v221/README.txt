V221 LEFT HEAD TILT: WALKING + JOGGING

Corrects v220 misunderstanding: undo head translation, X restored to0cm.
Both left walking/jogging BodySettings Head Roll0->+3degrees (character-left).
Rotation degrees, not cm. Other rotations and positions unchanged.
Based on v219 with both right-head roll corrections retained.
Same grey walking NPC and blue jogging NPC; F6/F7 edit blue jogger.
Extract fresh folder to load updated active presets. Native test NOT RUN.

V219 WALKING RIGHT HEAD ROLL

Same adjustment as v218 jogging, now also applied to raised WALKING right lean:
MLWalkingLeanPreset > RightLean > BodySettings > Head > Roll: 20 -> 0 degrees.
Pitch4.6/yaw-3.3 retained. Left lean and every other walking value unchanged.
V218 jogging correction retained exactly; other preset banks unchanged.
Same two raised AK74 NPCs/F6/F7 blue jogging editor/native camera.
Extract fresh folder; don't overwrite active profile with an older preset.
Offline package checks passed; native visual result not tested here.
This changes a saved additive roll, not an absolute head animation lock.

V218 RIGHT JOG HEAD ROLL TEST

Uses the user's newly uploaded MLJoggingLeanPreset.json for BOTH sides.
Only edit to that upload: RightLean > BodySettings > Head > Roll: 20.0 -> 0.0.
Head pitch 4.6 and yaw -3.3 retained, as are all weapon/arm/body values.
Original upload included as MLJoggingLeanPreset-OriginalUpload.json.
Left side unchanged from upload. All other 14 approved banks unchanged.
Same grey walking reference and blue editable jogger. F6/F7 edit blue jogger.
V217 native look isolation retained; no additional graph/aim/weapon changes.
This removes the saved extra 20-degree roll, not an absolute head-track lock.
Native DayZ compile and resulting visual orientation still require testing.
Extract as a NEW folder and launch there; don't copy an old profile over it.

V217 HEAD LOOK-TRACKING ISOLATION TEST (based on v216)

Same two raised AK74 NPCs: grey walking, blue jogging; F6/F7 edit blue.
All 14 approved preset files and experimental jogging seed remain byte-identical.
During custom armed leans, native idle/move/turn look overlays are disabled.
Ctrl+F1 native comparison keeps native look; outside leaning, look remains native.
Old automatic NPC-to-player head-reference corrections now output zero.
F6 head and F7 neck/head edits still operate; gun aim inputs are unchanged.

LIMITATION: this is NOT an absolute head-track replacement. JSON entries remain
additive. Native gait/raise clips and inherited torso transforms may still move
the head. This build removes verified extra look/correction layers without a
per-frame bone feedback loop. Native DayZ compilation/rendering NOT RUN here.
Test both sides, aim up/down, turn, stop/start movement, and compare Ctrl+F1.
If unwanted head motion remains, a compiled head-only animation track override
is still required; do not call this a complete head lock.

RAISED-WEAPON WALK / JOG LEAN EDITOR - V216

ALL approved JSONs retained as exact bundled+active profile defaults, including
newly approved soda/bandage walking file. No lossy single-file merge/rebase.
Soda/bandage families use separate walking bank; flashlight remains unchanged.

ONLY TWO NPCs side-by-side1m, same Denis model and AK74:
GREY walks (native speed1) with weapon raised; BLUE jogs (native speed2) raised.
No ADS. Both lean LEFT/RIGHT together, switching target EVERY1SECOND after
12sone-time reference setup. During setup they begin moving at3s and hold sides
longer for native grip/reference calibration. Smooth transitions retained.
Root positions pinned for preview: walk/jog gait plays without travelling away.

F6 weapon/arms/head and F7 body edit ONLY BLUE JOGGER via new armed jogging bank.
Scoped swap around armed graph, not the lowered unarmed helper. Separate jogging
reference cache avoids reusing walking/standing arm geometry. New bank seed EXACT
approved MLWalkingLeanPreset.json; walking grey reference and all global player
routes remain unchanged. Native IK may constrain some edits to maintain contact.
Save BOTH sides+F6/F7 to Profiles/LeanMosin/MLJoggingLeanPreset.json.
Send that JSON to approve/apply jogging later. No global jogging rollout yet.
Selecting editor side holds BOTH NPCs on that side, while they keep their gaits.

Native camera and pose graph unchanged. Extract fresh; no other lean mod loaded.
Offline data/clock/gait/scope/cache/scene/PBO checks pass; native compilation,
actual jog/aim/grip/editor pose/root pin/FPS/stability need testing in DayZ.
