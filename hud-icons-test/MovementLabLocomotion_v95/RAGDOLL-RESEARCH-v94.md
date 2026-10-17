# DayZ 1.30 infected ragdoll investigation

Verified against official scripts e3dda95b2b9730bdc0dba931abb35304b484bbfc (Build 1.30.164078, Scripts Rev.127250), not a generic engine assumption.

- `scripts/3_game/human.c`: Human exposes PhysicsSetRagdoll(bool), PhysicsIsRagdoll(), GetBoneIndexByName. The current 1.30 revision separately exposes PhysicsSetSimpleDeath for the old death system. Earlier conclusions based on older comments were incomplete.
- `scripts/3_game/entities/dayzinfected.c`: DayZInfected exposes animation death types and commands, but has no Human ragdoll switch. Selecting ANIM_DEATH_IMPULSE does not prove articulated physics activation.
- `scripts/1_core/proto/envisual.c`: SetBoneGlobal can set a named/mapped bone pose. Generic GetBoneIndex is demonstrated for Spine2 in the native HUD.
- `scripts/3_game/entities/object.c`: model/world-space bone transforms are readable.
- `scripts/1_core/proto/enentity.c`: entity root transforms are readable/writable; replacing a visual is possible, but swapping an infected mesh directly onto Human would rely on unverified model/ragdoll bindings, so v94 leaves the Human model alone and drives the original infected visual instead.
- `scripts/1_core/physics/physics.c`: generic rigid bodies, per-bone physics handles and joints exist. A full custom jointed solver is another potential route, but exposed APIs alone do not supply a configured infected physics skeleton.
- Official DayZ-Samples contains no infected ragdoll example. Public web search was inaccessible in this environment; no external mod claim was inferred from that.

Prototype: hidden Human physics driver + model-space named bone transfer to original infected body. Runtime gates require essential bones, sufficient matches and actual Human ragdoll activation. The corpse's animation is suspended only after physics activation is confirmed. Delete both entities on the existing replacement timer.

Unresolved runtime questions: bone binding axes, SetBoneGlobal behavior with frozen infected simulation, Human native physics interaction with hidden rendering, root/bone transform alignment, collision coverage, and visual deformation. These require native playtesting; C++ mocks cannot answer them.

Official sources:
https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/e3dda95b2b9730bdc0dba931abb35304b484bbfc/scripts/3_game/human.c
https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/e3dda95b2b9730bdc0dba931abb35304b484bbfc/scripts/3_game/entities/dayzinfected.c
https://github.com/BohemiaInteractive/DayZ-Script-Diff/blob/e3dda95b2b9730bdc0dba931abb35304b484bbfc/scripts/1_core/proto/envisual.c
