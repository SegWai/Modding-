MovementLab v84 - target timing and explicit NPC knockout

Male: upright at spawn, whole-body ragdoll starts on death; disable ragdoll and simulation four seconds after EEKilled. Replace the corpse with an upright male eight seconds after death observation. Hands/feet cannot be independently disabled through the exposed script API: only PhysicsSetRagdoll(bool) exists, so NO selective limb physics change is claimed.

Female: damage remains vetoed to prevent death. Queue positive global health damage; if unavailable use the hit zone health damage, then GetHighestDamage. Apply accumulated damage outside the pre-damage callback to a separate remaining-health counter and visible health. At exhaustion retain one health, explicitly StartCommand_Unconscious(0) for this uncontrolled NPC, initialize the unconscious state and start its five-second timer. Physics ragdoll enabled during knockout, disabled before health restore/native recovery. Added hit and knockout logs. Additional hits while down/recovering do not restart the timer. Both spawn conscious with ragdoll off.

Global-damage-first accounting preserves native global damage when supplied; zone/highest fallbacks may differ from stock global health-transfer scaling. Logs are needed if incoming damage is still zero or the unconscious physics/recovery transition fails. No in-game verification was available here.

Native camera/locomotion graphs, loadout and Gunter unchanged. Extract into a fresh folder. Native compilation, death timing and NPC unconscious/wake/stand behaviour need local testing.
