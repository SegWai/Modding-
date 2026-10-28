AMBIDEXTROUS LEAN - EXPERIMENTAL V4

FIX FOR CAMERA-ONLY SWAP:
V3 let the camera follow the REQUEST even when the weapon pose was inactive.
V4 changes camera side ONLY when the left arm/hand/weapon graph is active.
Pending/rejected/unready left pose keeps camera right; it cannot falsely imply
that the gun has changed hands. State-change diagnostics go to logs, not popups.

Neutral bone axes are now collected AUTOMATICALLY on spawn before guns are
created, then the same AK74/SKS/Glock/backpack loadout equips normally. Stand
centred for the brief setup. No manual stow is normally required. A5second
fallback still equips guns if neutral setup fails; logs report this condition.
No forced player stance/raise/lean/camera-look/movement inputs are added.

Raise your weapon, aim roughly level, and press your bound side mouse button.
First-use weapon/stance/gait/lean/ADS context briefly samples the original pose,
then activates the mirrored arm/hand/finger pose and left-hand weapon publisher
TOGETHER with the left camera. Press again to return to right.
If the pose cannot solve, camera stays right and logs give the waiting/rejected
state. Send Collect-Logs ZIP if this happens, or if gun remains right even with
left camera: that would isolate the native left weapon publication itself.

Controls: MovementLab - Shoulder swap / Shoulder swap (ambidextrous test).
Default Mouse4; bind preferred physical side button and clear its old action.
Default DayZ third-person height/distance, no NPCs, original saved lean186 and
all4approved JSONs unchanged. Newleft graph/IK exactlyv3: this change fixes
activation/setup, not an unverified native left-hand IK profile interpretation.

This remains raised-pose experimental. Reload/lowered/action clips stay native
right-handed. Native hand/weapon contact, ADS, firing/muzzle and FPS need testing.
V3userreport establishes game loads and camera action works; it does NOT prove
that the left weapon IK publisher functions. Offline checks cannot prove that.
