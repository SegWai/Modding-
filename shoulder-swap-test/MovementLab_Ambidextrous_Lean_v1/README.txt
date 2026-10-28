AMBIDEXTROUS LEAN - EXPERIMENTAL V1 (SEPARATE FROM SAVED LEAN V186)

Your original lean mod is preserved at Git commit3aff8a4 / tag lean-mod-saved-v186.
Run this separate ZIP by itself; do not load both copies of the pose workspace.
All FOUR approved pose JSONs are byte-identical to the saved lean mod.
No NPCs. Same player/native AK74/SKS/Glock/backpack. Third-person camera height
and distance are now DEFAULT DAYZ: the inspection4m/dropped/raised pivot override
was removed. Side switching uses DayZ's camera-side API only, no height/distance.

BUTTON SETUP (ONE TIME):
DayZ Options > Controls > MovementLab - Shoulder swap >
"Shoulder swap (ambidextrous test)".
Default is Mouse4 (first side button). Click the binding and press your preferred
side button if it is the other one. Clear that button's OLD action in Controls
so it does not trigger both actions. This mod does not edit your existing
control/profile files or silently remove an unknown original binding.

FIRST TEST:
1. Stow the gun, stand still upright with empty hands and no lean for half a
   second. This samples your own neutral bone axes ONCE, including fingers.
2. Equip AK74 and raise it without ADS, aim level, stand centred.
3. Press the bound side button. First-use context samples the original unswapped
   pose with new output ZERO, then applies the opposite arms/hands/head/fingers
   and publishes the weapon from the LEFT hand; camera follows to the left.
4. Press again to return to right. Then test crouch, left/right lean and walking.
   Each new weapon/stance/gait/lean/ADS context needs a brief level-aim sample.

WHAT THIS TEST IMPLEMENTS:
- Full anatomical left/right arm/hand/finger exchange, not a camera-only toggle.
- Bone-basis-safe reflected deformation relative to YOUR neutral skeleton.
- Mirror plane follows chest deformation; approved torso/legs/lean stay unchanged.
- Cached corrections before existing late native aim, left primary weapon IK
  publication and right support chain, original weapon inventory/FSM retained.
- No weapon clone, inventory detach/delete/teleport, or per-frame pose feedback.
- Aimed direction input, firing and weapon state remain native. FP/TP share pose.

EXPERIMENTAL LIMITS / WHAT STILL NEEDS TESTING:
Native Windows compilation, input registration/button names, left-anchor weapon
IK profile interpretation, contact, ADS alignment, actual muzzle/projectiles,
firing/recoil, clothing and FPS have NOT been tested here. Offline math/PBO
checks are not proof that this left-hand weapon profile renders/fires correctly.
This first test swaps the RAISED pose. Lowered/reload/interact animations still
use native right-hand clips; no left-handed reload/action clips were authored.
New contexts briefly show native unswapped pose while sampling. This is not a
finished ARC Raiders animation/transition system. Report the first observed fault
with Collect-Logs and a screenshot/recording before trusting firing/ADS behavior.

F6/F7 remain the original unarmed preset editors. Mouse shoulder action is
ignored while a menu is open. Use the launcher included with THIS separate kit.
