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
