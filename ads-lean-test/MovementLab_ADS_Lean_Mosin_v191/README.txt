LOWERED AK74 GRIP REPAIR - V191

Same synchronized red armed/blue custom-unarmed preview, fixed-left experiment
NOT included. Native third-person camera retained. F6/F7 target red only.

Fresh MLHeldLeanPreset arms start at native lowered AK74 posture: only its F6
arm rotation fields and F7 shoulder/arm/forearm/hand fields are zeroed. Torso,
head, legs retained. This changes ONLY the experimental held editor bank, not
any of your four approved preset JSONs or the blue reference NPC.

Held branch now evaluates native grip ONCE, AFTER body/editor corrections,
using the original NormalWeaponIK configuration, RightArm rotator, ArmIK masks
and native output policy. Removes the incorrect raised-profile publisher.
Empty-handed path still evaluates original grip stage before original body.
F6/F7 arm edits remain available; native IK can constrain them to maintain grip.
F6 gun XYZ/PYR still not implemented; use body/arm/head editor controls.

Extract fresh, do NOT copy old MLHeldLeanPreset.json from v190 into this test.
Save the new red pose to Profiles/LeanMosin/MLHeldLeanPreset.json.
Offline graph/preset/source/PBO checks pass. Native compile, actual lowered grip,
mesh, editing response and gameplay stability still need an in-game retest.
