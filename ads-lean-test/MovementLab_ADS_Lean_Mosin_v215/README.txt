APPROVED SODA / BANDAGE WALKING DEFAULT - V215

Uploaded MLSodaCanWalkingLeanPreset.json preserved EXACTLY. Default for upright
LOWERED WALKspeed1 with soda-can and bandage holding families, including soda
can variants, BandageDressing, and Lassi containers sharing soda-can ASI.
Native ONEHANDED guard+player_main_1h_sodacan / player_main_1h_bandage instance
matching; native SodaCan_ColorBase/Lassi_ColorBase/BandageDressing subclass
fallback if instance string unavailable. Modded items reusing ASIs also match.
Bandage has a distinct ASI; included explicitly by user approval of this bank.
Not every ONEHANDED object: Flashlight/Compass/etc retain prior defaults.
Rags,water bottles,canteens and generic1h items are not assumed identical.
Standing soda/bandage poses and raised/crouch/run routes unchanged.

Scene still ONLY grey soda can + blue bandage, walking in place on same clock.
BOTH now use this approved shared bank. F6/F7 edits affect BOTH and eligible
player item poses; flashlight bank remains independent. Save BOTH sides/F6/F7
in Profiles/LeanMosin/MLSodaCanWalkingLeanPreset.json.
All thirteen earlier approved files and pose graph/native camera unchanged.
Native item IK still adapts grip. F6 item-offset rows remain unsupported.

Extract fresh. Offline raw/profile/category/cache/scene/PBO checks pass; native
compile, animation-instance query reliability, item grip/visiblepose/gait and
stability require in-game testing. Native-family fallback preserves vanilla scope.
