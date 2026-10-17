MovementLab v95 - infected mesh on the physical actor (experimental)

Observed v94 failure: human helper rendered visibly and ragdolled; the original infected stayed in its pre-death pose. That proves the physics driver can activate, not that SetBoneGlobal transfers its pose. This build removes all manual bone-copy code.

On the one infected's confirmed death, create a Human actor but explicitly hide it using camera mask zero and VISIBLE flag clearing, not SetInvisible alone. Replace its visual with the original infected VObject, copy selected textures/materials, then activate its Human ragdoll. Confirm both the infected visual handle and actual native ragdoll state before hiding/suspending the original zombie corpse. Reveal only the infected-mesh physical actor. Reassert visibility flags every mission update. If native code restores the survivor mesh, immediately hide/delete the proxy and restore the original corpse. No native infected death animation is overridden.

The candidate change is direct mesh-on-physics binding instead of manual writes to a frozen infected skeleton. It MAY still fail if the infected mesh cannot bind to the Human physical skeleton, show distortion or remain rigid. Handle equality plus PhysicsIsRagdoll does not prove correct visible deformation. No native compiler/game runtime is available here. Local testing remains essential; this is not claimed as fixed.

One visible infected fixture remains, alive until killed, with confirmed-death five-second replacement. Replacement/shutdown delete the helper before removing the original body. Other NPCs/locomotion/camera/Gunter/grenades unchanged.

Extract into a fresh folder. Kill the zombie and check whether there is a single infected-looking body with independently falling limbs. Collect logs if the mesh-swap, activation, or mesh-changed fallback appears. Old v94 research notes are retained as historical context and superseded by this readme where behaviour differs.
