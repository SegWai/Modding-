V184 - SYNCHRONIZED UNARMED LEANS, MIRRORED CUSTOM UPPER BODY

RED: native/default unarmed standing lean, read-only.
BLUE: custom UPPER body; native pelvis/legs/feet, without the old custom stance.
Same empty hands, Denis model/scale, clothing and 0.5m spacing as183.
Both get the SAME private lean input: left/centre/right/centre, one-second targets.
The native lowered-lean expression uses this input on these NPCs only; it no
longer depends on the engine-owned Lean float retaining the scripted value.
No weapon, ADS or raised-arm state is enabled. Natural pose height retained.

Your uploaded RIGHT unarmed edits are preserved. LEFT is now the anatomical
mirror of RIGHT: upper-body base AND shoulder/arm/forearm/hand/head edits,
swapping left/right parts and reflecting lateral position/yaw/roll.
The custom upper body is attached relative to the current native pelvis;
no saved custom pelvis/leg/foot corrections are applied by the base layer.
Lower F7 offsets start at zero; you may still edit those explicitly if desired.

F6: direct upper-arm/head rotations. F7: all24 body parts XYZ/rotations.
Opening either panel holds BOTH NPCs on the selected side; edits affect BLUE only.
RMB navigation retained. Save All writes MLUnarmedLeanPreset.json (both sides).
Uploaded original is archived; mirrored initial preset is bundled/active.
Standing-aim, walking-aim and approved crouch JSONs are preserved byte-for-byte.
Extract fresh so an older active profile cannot override this mirrored save.
Let both sides run once for native upper-body references to settle.

Offline reflection/lower-body isolation/shared-input/graph/PBO checks passed.
Native DayZ compilation, rendered reference lean, posture/cloth/FPS need testing.
