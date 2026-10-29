# Separate first-person and external character poses

Status: implementation blocked; v225 does not satisfy simultaneous poses.

Required behavior

- Actual character skeleton always uses approved custom standing/walking/jogging/crouching poses.
- Local first-person arms/weapon display uses native crouch-style upper lean.
- Freezing while in first person and inspecting externally must show custom pose.
- Other clients always see custom pose. Camera selection must not change the actual skeleton.
- Preserve saved custom head settings; absolute native-head replacement remains separate unfinished work.

Evidence from current code

v223-v225 ML223FirstPersonOnly selects two animation sources on the SAME character
skeleton. Local-only selection avoids sending FP camera mode to other clients but
cannot create two simultaneous local skeletal poses. MLFreeze135 disables the
actual character simulation; this also freezes the selected first-person pose.
This is an architectural mismatch, not another preset offset error.

Public SDK inspection

scripts/3_game/dayzplayer.c DayZPlayerCameraResult exposes m_fInsideCamera
(inside LOD selection), m_OwnerTM/m_bOwnerTMOverride (whole-owner rendering matrix),
and camera/bone attachment transforms. These are not a second skeletal animation
palette. scripts/3_game/entities/camera.c exposes Camera.GetCurrentCamera for
external script camera detection. Detecting that camera can switch an unfrozen
pose back but does not meet the simultaneous-model requirement.
No supported separate per-view skeletal override was found in inspected public
Human/DayZPlayer/Entity APIs. Generic bone setters were previously rejected for
human skeleton posing; do not revive that approach or corrected-output feedback.

Implementation needed

1. Keep real actor graph permanently on approved custom path.
2. Build separate client-local first-person arms/weapon visual asset and animation
   representation. This must not replace the gameplay weapon or actual character.
3. Implement camera-only visibility/lifecycle, clothing/weapon attachment support,
   aim/ADS/reload/recoil synchronization, and exact native lean retargeting.
4. Ensure no duplicate damage, inventory, projectile, collision, sound or shadow
   behavior from a proxy. An independently animated PlayerBase clone is not a
   verified viewmodel solution and risks those side effects.
5. Compile native visual/skeletal assets with Windows DayZ Tools and test in game.
6. Validate freeze in FP then external inspection, normal camera changes, standing/
   walking/jogging/crouch, weapon changes, ADS, respawn, and a second client.

Available cloud workspace has no Windows DayZ Tools compiler or running DayZ.
A true viewmodel has not been built or tested. Do not publish another skeleton
switch as a completed solution. No new runtime build accompanies this note.
