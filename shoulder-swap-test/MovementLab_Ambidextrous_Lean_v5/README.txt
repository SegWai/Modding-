AMBIDEXTROUS LEAN - EXPERIMENTAL V5

V4 recording confirms weapon/hand/camera swap activates, but the rifle is rolled
and the support arm does not agree with the gun. V5 changes TWO publisher fields:
- weaponaxis back to native -x: this is a WEAPON MODEL axis, not a hand-side flag.
  Changing hands must not reverse the unchanged gun model's native axis.
- Secondary chain solve OFF in the left-hand publisher. That old native target
  was authored for LEFT support hand on a right-handed weapon; applying it to
  the new RIGHT support arm overwrote the mirrored hand/forearm pose.
Both arms/hands/fingers now keep the same mirrored pose; publisher follows the
left trigger hand without independently overriding either arm chain.

Same side mouse binding, automatic neutral setup/equip, synchronized camera,
native third-person height/distance, no NPCs, all4approved presets unchanged.
Original saved lean186 untouched. No new pose/hand sliders or extra offsets.
Raise gun and test centred left shoulder, then left/right lean and walking.

One-shot READ-ONLY log after a settled swapped pose records original/left sight
position+forward/up and both wrist positions, to identify remaining weapon roll
or grip offsets. This NEVER feeds corrected data back into the pose solver.
If contact/orientation is still wrong, send a recording AND Collect-Logs ZIP.

Offline checks/PBO packaging passed. V5 native compilation/rendered roll/contact,
actual muzzle/firing/ADS/performance are NOT RUN here. This is still raised-pose
experimental; lowered/reload/interact clips remain native right-handed.
