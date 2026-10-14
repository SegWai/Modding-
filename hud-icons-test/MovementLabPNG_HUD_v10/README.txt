MovementLab image-based stance/speed HUD v2

Close DayZ. Extract the ENTIRE ZIP into a NEW folder and run Launch-Movement-Test.cmd.
This is a complete separate test package, not a PNG to copy into another version.
Steam must be running. The launcher prepares the existing movement workspace and
loads your installed SNAFU Weapons pack. If it cannot locate the mod, put its
local folder path in SNAFU-Mod-Path.txt as described by Configure-SNAFU.ps1.

The old five text bars are replaced by a blue-backlit silhouette tile and a
stance/level label, next to the existing stance/noise indicators.
The tile shows the selected level, including a queued scroll destination.
It does not force achieved animation/gait to jump to that level.

24 image selections:
- Crouch movement: levels1-5.
- Crouch aiming: levels1-4.
- Standing idle and crouch idle (not aiming).
- Walking: levels1-2; jogging: levels1-2; full sprint.
- Run-to-crouch momentum fade: its locked transition tile plus AUTO label.
- Slow walking aim: levels1-3; level3 is the extra matching150% tile you requested.
- Fast walking aim: levels1-3.
- Sprint-to-aim140%-100% momentum fade: its locked tile plus AUTO label.

The approved chart actually has23 tiles despite its old22 caption; the new slow
aiming level3 brings this package to24. Existing speed levels/values and timers
are unchanged. Jogging labels use level1/2 within jogging (the prior five-bar
standing range used positions3/4). Aiming still displays the appropriate aiming
tile when stationary. Non-aiming shows idle only when movement reports idle.
Prone keeps the native stance indicator; no unrequested prone image is substituted.
HUD hidden/death/unconsciousness/disabled mod hides the custom image too.

Art comes from the approved reference-style chart, encoded as individual native PAA textures.
Each tile is a separate PAA texture, excluding chart headings and captions.
There is no SetUV call or custom UV array. Textures are preloaded once into hidden
image widgets; only the active widget changes when the indicator changes.
The extra slow-aim level3 is a separately generated matching tile.
ImageSources includes both original PNGs, the source pixel mapping and individual texture metadata.

Checked in cloud: all24 actual selection mappings, both momentum branches,
HUD visibility/failure paths, cached updates, placement bounds and source identity
of unchanged movement logic. All24 individual PAA textures decode with an independent reader.
Native DayZ Enforce compilation, texture presentation and placement need the
local DayZ test. If images are distorted, blank or absent, send a HUD screenshot
and run Collect-Logs.cmd; output is MovementLab-HUD-Icons-v2-Logs.zip.

Current SNAFU loadout and five filled spare mags/no loose ammo are retained.
The optional F9/F10 static arms test is retained, starts OFF and is unrelated to
this HUD change; its original limitations are in README-Previous-Arms-Test.txt.
Your previous versions are preserved.
