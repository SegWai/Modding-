v2 fixes the native compile error: no SetUV arrays or custom UV calls remain.
The approved chart tiles are extracted by the asset packer (not redesigned),
fitted proportionally on256-square or512x256 canvases and encoded as standard
DXT5 PAA with full mipmaps. Artwork, stances and level mappings are unchanged.
The original PNGs and source rectangle map are included for reproducibility.
individual-textures.json describes every resulting resource.
All24 files are loaded once into24 widgets; only the selected widget is visible.
Rebuild: python tools/build_hud_icon_textures_v2.py then check_hud_icons_v2.py
and package_hud_icons_v2.py. Windows native rendering remains to be tested.
