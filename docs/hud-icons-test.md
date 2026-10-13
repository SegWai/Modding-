# Image-based stance and speed HUD

Package: `artifacts/MovementLab_HUD_Icons_v1.zip`.
Source: `hud-icons-test/MovementLabHUDIcons_v1`.

Replaces the five text bars with the approved reference-style tiles. The chart
actually contains23 tiles (its old caption says22); the user requested a third
slow-aiming tile for the existing150% level, bringing the HUD to24 images.
`ImageSources/icon-map.json` records each ID, source pixel rectangle, texture
slot and UV bounds. The primary chart is reused, not redrawn; no caption/headings
are included in the selected tile region. The extra image was generated using
the primary chart as its style reference.

The only World change is a read-only `MovementLabGetHUDIcon` accessor next to
the existing speed getter. Selected targets drive images, not achieved gait.
Actual non-aiming idle selects standing/crouch idle; aiming retains its selected
aim tile when stationary. Crouch and sprint-to-aim momentum flags select their
locked tiles. Jog internal global steps3/4 are presented as jog levels1/2.
Prone uses the native stance indicator without a fabricated custom tile.

The HUD creates one ImageWidget and one label next to native noise/stance panels.
It loads two PAA textures once and updates image slot/UVs only on an icon change.
Aspect ratios are preserved, including wider transition illustrations.
AUTO retains the existing gold text cue. Native HUD hiding, death, unconsciousness
and disabled MovementLab hide the custom panel. Missing textures/widgets or
wrong texture dimensions keep it hidden and log the failure.

Source images are encoded at original pixel resolution on power-of-two canvases,
with standard DXT5 PAA mip chains and16-entry mip offset metadata. This is texture
encoding/padding, not silhouette editing. Texture construction uses Pillow12.3.
An independently compiled armake paa2img reader successfully decoded both files:
mean original-region RGB compression error3.699/255 and2.225/255. No armake code
or executable is bundled in the mod.

`tools/check_hud_icons_v1.py` executes the actual accessor and HUD translated to
C++ with engine mocks, checking all24 selections/UVs, cached updates, AUTO states,
idle transitions, visibility, dimensions, reinitialization and failure paths.
It also compares movement World code after removing only the new accessor,
mission code and remaining scripts against the preceding arms-only test.
The packer verifies source/PBO bytes, offsets and SHA1 footer. Native Enforce
compilation, UV orientation and in-game appearance still require DayZDiag.

The SNAFU loadout and optional F9/F10 arms prototype are inherited unchanged;
the latter starts off. Their earlier native-test limitations remain. Existing
versions and the user's untracked arm-lift asset directory are preserved.

Rebuild:

```
python tools/build_hud_icon_textures.py
```

Insert `ImageSources/generated-uv-method.txt` as the `MovementLabSetIconUV` method
in the HUD controller if the artwork/map changes, then:

```
python tools/check_hud_icons_v1.py
python tools/package_hud_icons_v1.py
```

## v2: native UV compile failure

The uploaded `MovementLab-HUD-Icons-v1-Logs.zip` confirms the native Mission
compiler rejects the argument to `ImageWidget.SetUV` with "Incompatible parameter
'uv'". The C++ mocks did not reproduce Enforce's multidimensional-array parameter
handling, so their passing result did not validate that API call.

`MovementLab_HUD_Icons_v2.zip` removes SetUV, CUSTOMUV and all UV arrays entirely.
The approved tiles are extracted during asset packaging, fitted proportionally
onto256-square or512x256 power-of-two canvases, and encoded as individual PAA
files. There is no artwork redesign.24 ImageWidgets preload one resource each;
only the selected widget is shown. This stays within each widget's image-slot
limit and avoids scroll-time texture loading. No World/mission code differs from
v1. Existing v1 is retained for diagnosis.

All24 files pass independent armake decoding and mip/header checks. The actual
accessor/HUD mock tests cover selections, one visible image, cached updates,
reinitialization, AUTO, hiding, placement and failures. Those checks remain
distinct from native Enforce compilation/rendering, which require the next
DayZDiag test. The offending interface is removed rather than treated as proven
by the C++ harness. Collect-Logs now writes MovementLab-HUD-Icons-v2-Logs.zip.

Rebuild v2:

```
python tools/build_hud_icon_textures_v2.py
python tools/check_hud_icons_v2.py
python tools/package_hud_icons_v2.py
```
