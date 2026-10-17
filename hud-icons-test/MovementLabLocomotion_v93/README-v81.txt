MovementLab v81 - repeatable range targets

Male: normal damage/death, native death collapse settles to a fixed corpse (forced physics-ragdoll override removed). Five seconds after death is observed, remove the corpse and spawn a fresh standing male at the recorded death location. No accumulating corpses.

Female: Eva, red hoodie, blue jeans/shoes, beside the male. Damage is vetoed before applying even lethal headshots; an incoming hit requests native unconsciousness. The five-second timer starts at OnUnconsciousStart; additional hits while down/recovering do not extend it. At the deadline health/blood/shock are restored and native wake-up is requested, followed by native standing-up. Wake and standing animations take their normal time. She is not replaced or killed. Uses reversible native unconscious collapse, not forced live-body physics ragdoll.

Both remain stationary and offline-only. Gunter, body-relative look limit, locomotion and loadout retained. Existing camera and animation graph files are unchanged. Extract to a fresh folder. Native compilation, target death/respawn, nonlethal damage protection and recovery animations still require local DayZ 1.30 testing.
