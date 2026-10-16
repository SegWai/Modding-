v51 rebuilt from v42, excluding v43-v50 stationary-look experiments.
Stationary, not aiming: automatic native free-look; head and camera yaw limited to +/-90 degrees. No Alt hold needed. The body receives no scripted rotation or automatic turn request. Applies upright/crouch/prone when stationary; prone on back, rolls, stance transitions and actions retain native controls. Movement/aiming release this mode.
Uses native camera UpdateLRAngleUnlocked with tighter yaw bounds and per-player SetLookLimits. Excess input is discarded at the cap. No custom yaw accumulator, heading model, animation graph edits or camera transform writes.
All v42 files byte-identical before packaging, including movement, sway, HUD icons, graphs and MMG/SNAFU loadout.
Native override signature and float32 boundary/reversal checks passed; native DayZ compilation, visible head pose and root stability still require local testing.
