Lean range v41 — custom raised first-person pose with smoother transitions

Extract into a NEW folder and run Launch-Mosin-Lean-Test.cmd.
Project root F:\DayZProjects. Stand neutral briefly for existing height calibration.

Restores the approved custom raised-weapon pose in BOTH first and third person, including raised aiming without ADS. Enabled by default. The v40 camera restriction is removed. Native ADS controls/cameras stay unchanged.

Targets the snap with shared visual-transition smoothing: lean input is rate-limited over0.18s per unit, custom movement weights blend over0.20s, and the final native grip/aim solver blends over0.22s instead of0.08s. Native locomotion clip/speed/state-machine expressions remain unchanged. All corrective Amount values and the complete standing/full-walk left/right pose endpoints remain unchanged at matching inputs. Player and NPC share the smoothing.

F8 now toggles custom raised-weapon pose in both views; starts ON. F5 reference hold/elbow comparison; F6 head comparison; F7 native/custom; F9 view/mode and lean_requested/lean/move_blend diagnostics; F10 patrol pause. The95% height controller and range loadout/ammo/ragdoll/respawn remain.

Test raised first person WITHOUT ADS: start/stop strafing and release/reverse Q/E. Then compare third-person full lean. Native transition smoothness and grip during blends still need an in-game check. If a snap remains, press F9 near it and send Collect-Logs.cmd ZIP plus video. Included PNGs remain historical v32 authoring previews.
