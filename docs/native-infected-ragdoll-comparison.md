# Native infected ragdoll investigation — 18 October 2026

The supplied Part-01.zip contains 202 assets with verified manifest sizes and SHA256 hashes. The comparison now reads the actual embedded ODOL56 skeleton tables rather than treating animation XML declarations as mesh skeletons. No gameplay files were changed by this investigation.

## Findings

| Model | ODOL version | Skeleton bones | Missing ragdoll bones | Invalid ragdoll ancestry |
|---|---:|---:|---:|---:|
| bodyparts_above0.p3d | 56 | 159 | 0 | 0 |
| m_denis_2.p3d | 56 | 159 | 0 | 0 |
| hermit_above0.p3d | 56 | 159 | 0 | 0 |
| hermit_newbindpose.p3d | 56 | 159 | 0 | 0 |

All four ordered name/parent tables are identical. Each uses `DayzTemporarySkeleton`. The 95-bone infected and 172-bone human declarations in skeletons.anim.xml describe different animation skeleton declarations; those counts alone are not evidence that the actual models are incompatible.

human.ragdoll defines 11 physical bones, with mass values summing to 73.9. All names exist in all four models. Each physical parent is an ancestor in the model skeleton (intermediate nonphysical bones are allowed). The definition contains pelvis, spine3, head, upper arms, forearms, thighs and shins. Hands/feet do not have standalone RagdollBone declarations; foot capsule geometry belongs to the shin rigid bodies.

This is structural evidence only. Mesh weights, rest/bind matrices, coordinate conventions and native physics loading have **not** been proven compatible. The bounded parser intentionally does not guess matrices from arbitrary binary floats.

## Controller boundary

The official DayZ-Script-Diff revision `e3dda95b2b9730bdc0dba931abb35304b484bbfc` exposes `Human.PhysicsSetRagdoll(bool)` and `PhysicsIsRagdoll()`, alongside the older `PhysicsSetSimpleDeath`. `DayZInfected` instead inherits `DayZCreatureAI` and exposes `StartCommand_Death(int,float)`; no equivalent infected ragdoll switch appears in the inspected script declarations. This does not establish that the closed engine cannot do it. It establishes that the working Human call cannot simply be called on an infected instance.

The uploaded zombie config selects simulation `dayzinfected`, skeleton `hermit_newbindpose.xob`, and meshObject `dz/characters/zombies/z_hermit_m.xob`. No ragdoll binding was found in the collected infected config/graphs. The Human ragdoll definition references `{D470A4E7581CCE23}DZ/anims/workspaces/player/Models/player_m_editorpreview.xob`. No loading rule for that definition has been established; inventing a config property is not a fix.

v94/v95 proxy attempts remain failed user tests. Neither skeleton compatibility nor Python tests demonstrate that a zombie will fall with native articulated physics. No further proxy gameplay build was made.

## Concrete missing inputs discovered in the inventory

The first collector inventoried, but excluded, these existing files:

- dz/anims/workspaces/player/models/player_m_editorpreview.xob (374049 bytes)
- dz/anims/workspaces/infected/models/z_hermit_m_editorpreview.xob (137302 bytes)
- dz/characters/zombies/z_hermit_m.xob (137230 bytes)
- dz/characters/bodies/player_testing.xob (9638 bytes)
- player/infected sync tables and workspace metadata.

Collector v2 includes these and the related editor-preview models. No new extraction is expected because the first inventory already located them. Inspecting these can clarify the source skeleton/bind representation; it does not guarantee a configurable infected ragdoll loader. Native loading and activation ultimately require DayZ Tools/game testing, which is unavailable in this Linux environment.

## Reproduce

Run `python tools/compare_ragdoll_skeletons.py Part-01.zip --output comparison.json`. It reuses the manifest/hash validation in audit_ragdoll_assets.py. The derived output is in native-skeleton-comparison.json; original models are not redistributed.

Parser verification: `python tools/check_native_skeleton_comparison.py` (7 tests), `python tools/check_rig_asset_audit.py` (12 tests). Covers malformed/truncated skeleton tables, missing/cyclic parents, duplicate bones, unsupported versions, ragdoll nesting and the collector selection gap.

Independent format cross-check: KoffeinFlummi/armake revision `e4940fae0d28c4dd07d9d2c591f8e056545fee3f`, src/p3d.c `write_skeleton`, writes the same name/flag/count/name-parent/terminator layout. That project writes a newer ODOL version and is not a complete DayZ56 decoder; its layout is corroboration, not proof of the rest of the file format. The comparison parser was written for this investigation without copying that implementation.

## Follow-up

The second upload supplied the omitted XOB files. The transform comparison is now recorded in [infected-xob-bind-comparison.md](infected-xob-bind-comparison.md). Its shared physical-bone transforms agree closely; this earlier report's missing-XOB status is historical. Native controller activation remains unverified.
