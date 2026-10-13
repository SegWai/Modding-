Source artwork: approved reference-style chart plus generated slow-aim level3.
No game assets from SNAFU are included here.
Native textures: DXT5 PAA, power-of-two canvas, source-resolution pixels, standard
mipmap chain. Atlas UVs use padding-aware coordinates. BC3 compression introduces
small pixel differences; no character silhouette artwork was edited by the packer.
Independent armake decoder: primary image mean RGB error3.699/255; extra2.225/255.
Only the image atlas UV selection is performed in the running HUD.
Build: python tools/build_hud_icon_textures.py then tools/check_hud_icons_v1.py and
 tools/package_hud_icons_v1.py from the repository. Python requires Pillow12.3.
