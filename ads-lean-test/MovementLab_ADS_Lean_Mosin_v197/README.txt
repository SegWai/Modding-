APPROVED BAT LEAN DEFAULT - V197

Uploaded MLBatLeanPreset.json preserved EXACTLY as approved default.
Stationary upright LOWERED bat-style holding on player uses it. Baseball bat,
nailed/barbed/Christmas variants share player_main_2h_bat.asi. Native instance
matching supports modded items reusing the same holding profile; known native
bat subclasses are fallback if instance query not populated. TWOHANDED guard.
NOT every two-handed object: axes/shovels/sledgehammers have different profiles
and are intentionally excluded. Pistols/rifles keep their own approved banks.
Raised aiming/walking/crouch remain their previous routes.

Bat+blue NPC comparison/F6/F7 remain, now seeded with the approved bat file.
F6/F7 edits affect bat bank, including eligible player holding a bat; blue and
other approved banks stay separate. Save both sides to MLBatLeanPreset.json.
All SEVEN approved preset banks preserved. Camera/pose graph unchanged.

Extract fresh; do not copy old profiles over new approved default. Offline
native-profile/source/preset/scene/PBO checks pass. Native compile, animation
instance string availability, actual grip/visible pose/performance need testing.
