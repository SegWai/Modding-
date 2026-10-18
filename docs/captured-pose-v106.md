# v106 captured-pose bridge

The v105 report confirms that native ragdoll activation and root momentum do not establish pose continuity. Human stance preparation cannot reproduce infected arms, attacks or crawling reliably.

v106 removes that approximation. It snapshots up to 91 shared skeletal transforms before the infected death callback reaches the native implementation. A corpse-only branch in the player animation graph applies parent-aware rotation and translation corrections. The default gate is zero, preserving the normal player graph. Readback must match captured positions within 1 cm and basis vectors within 0.035 before physics activation. A separate immediate physics-seed diagnostic distinguishes graph matching from a possible native death reset.

This remains an infected-model Human corpse replacement, not a native infected physics controller. The original is frozen while the hidden replacement prepares; that delay may remain visible. Root velocity transfer is retained, but individual limb angular velocities are not transferred. Exact subframe continuity, native procedural-node conventions, compilation and performance are not verified in the cloud. Failure to match restores the original death path rather than publishing an unmatched replacement.

Validation: six offline pose-math tests and five graph/source integration tests passed. These do not substitute for a native test. Test idle/raised arms, attack, running and crawling deaths using the new v106 folder, then collect logs. Relevant markers are MLPOSE106 bound, applied, verify and physics_seed. Do not infer success from PhysicsIsRagdoll alone.
