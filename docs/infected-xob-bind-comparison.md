# XOB rig comparison — second upload, 18 October 2026

## Result

The second Part-01.zip verifies successfully: 218 assets, complete manifest, matching SHA256 hashes and sizes. All 202 files shared with the first upload are byte-identical. The 16 additional files include all ten selected XOBs and the previously omitted workspace/sync metadata.

The actual infected meshObject (`dz/characters/zombies/z_hermit_m.xob`) and the human model referenced by human.ragdoll (`dz/anims/workspaces/player/models/player_m_editorpreview.xob`) have nearly identical transforms for every one of the 11 physical bones. Under the observed XOB node-transform interpretation:

| Bone | Position difference (model units) | Rotation difference (degrees) |
|---|---:|---:|
| pelvis | 0.00000083 | <0.00001 |
| spine3 | 0.00000190 | 0.00001 |
| head | 0.00000406 | 0.00002 |
| leftarm | 0.00000145 | 0.00042 |
| leftforearm | 0.00000257 | 0.00047 |
| rightarm | 0.00000220 | 0.00012 |
| rightforearm | 0.00000199 | 0.00019 |
| leftupleg | 0.00000056 | 0.00005 |
| leftleg | 0.00000050 | 0.00015 |
| rightupleg | 0.00000058 | 0.00002 |
| rightleg | 0.00000022 | 0.00003 |

This substantially weakens the hypothesis that a large skeletal bind-pose discrepancy explains the failed ragdoll tests. Rebuilding or reweighting the whole zombie mesh is not justified by these results. It does **not** prove that the infected physics controller instantiates an articulated rig, or that assigning a human mesh to an infected/human proxy transfers that rig.

## Observed binary layout and checks

The uploaded XOBs have FORM/XOB6 envelopes and HEAD/LODS chunks. Envelope/chunk lengths agree exactly. The HEAD contains a string table, material-index entries and 36-byte node records. The observed node record is a string index, translation, XYZW quaternion, next-sibling link and first-child link. Its interpretation is inferred from these files, not confirmed by an official XOB specification.

All ten XOB node tables pass range, finite-value, quaternion norm, unique-name, cycle, parent-tree and reachability checks. The human male has 148 nodes; the female has 150; the actual infected meshObject has 92; infected editor-preview variants have 93. The extra editor-preview node is not evidence of another physical joint. Different node indexes must be mapped by name. Parent-relative transforms are composed before comparison; quaternion signs are treated as equivalent rotations.

The remaining HEAD/LODS data is intentionally not treated as decoded mesh weights or a physics rig. No model files have been modified, executed or republished. The report publishes only derived metadata, hashes and the 11-bone comparison.

## Native activation remains unresolved

No `ragdoll`, `.phys`, `.ragdoll` or PhysicsSet reference appears in the newly supplied XOB, AW or ASY data searched here. Both inspected human and infected XOBs contain HEAD/LODS top-level chunks, so chunk names do not establish a separate ragdoll loader. AW/ASY files supply animation workspace/synchronization data and do not reveal an infected ragdoll activation hook.

Current public script evidence remains: Human exposes PhysicsSetRagdoll/PhysicsIsRagdoll; DayZInfected has a separate native controller and death command. A skeleton-name or Object-path change alone cannot establish how that controller loads physical bodies. Generic physics/joint APIs are not proof of access to the animated infected's internal articulated rig.

The next decisive test requires the native DayZ runtime/Workbench: compare the live Human and infected physics instances before and after death (body/bone count, dynamic state, command/controller state and which physics resource is instantiated). The Linux workspace has neither the DayZ runtime nor its Windows native debugger/Workbench, so this step has not been performed. No new gameplay ZIP is presented as a working fix. The failed v94/v95 proxies remain failed tests.

No further asset collector run is currently requested. The files needed for this offline transform comparison are now present.

## Reproduce

`python tools/compare_xob_rig_transforms.py Part-01.zip --output xob-comparison.json`

The parser reuses the collector manifest/hash validation. `python tools/check_xob_rig_comparison.py` passes 9 tests covering truncated files, malformed links, unreachable nodes, material offsets, invalid quaternion values, duplicate names and transform composition. The actual upload also passes all ten XOB structural checks. Tests validate the parser, not native ragdoll behavior.

See [derived comparison](xob-rig-comparison.json) and the earlier [P3D skeleton comparison](native-infected-ragdoll-comparison.md).
