AMBIDEXTROUS LEAN - EXPERIMENTAL V7

V6 logs identify a DIRECTION/OFFSET mismatch, not just gun roll: forwarddot0.686
(about47degrees), updot0.992;5degree roll probe changed measuredframe0.00094deg.
Support target was unreachable. Repeating roll adjustment cannot fix that.
V7 removes that probe/support correction and changes the weapon anchor frame.

The visible LEFT trigger hand keeps its mirrored anatomical rotation. A separate
native skeleton animation helper bone named Weapon is positioned at that wrist,
with a cached conversion into the RIGHT-trigger coordinate frame expected by
DayZ's existing weapon IK profile. The publisher uses that helper, not a raw
left wrist with right-hand-only offsets. The RIGHT support arm keeps the mirrored
pose; no forced original-left-support IK or limb stretching is added.

The helper is reconstructed from native pelvis-local baseline and current left
wrist, never from its own corrected output. This tracks the last evaluated hand
pose; native same-frame attachment alignment/possibleone-frame tracking delay
must be checked in game. Helper bone's local transform is assumed constant in
raised locomotion; this is experimental, not a verified replacement IK asset.

Same side button, automatic neutral setup, approved4JSONs, no NPCs, native camera
height/distance. Stand still on first swap long enough for the original mirror
context to settle. No2second roll probe anymore. Source original lean186 saved.
Native skeleton includes Weapon/propweaponbones, but this new virtual anchor
WeaponIK configuration/load/render/contact/fire/ADS/performance is UNTESTED.
Do not load both standalone workspace mods. Reload/lowered/actions stay native.

Send Collect-Logs plus a screenshot/recording if still wrong. V7 logs compare
profile anchor, literal item transform, accessor sightframe and wrists to avoid
confusing a camera aiming frame with the actual rendered weapon attachment.
