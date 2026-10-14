from pathlib import Path
import sys,shutil,json
from psd_tools import PSDImage
from PIL import Image,ImageDraw
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];B=R/'hud-icons-test/MovementLabPSDHUD_v2';S=R/'hud-icons-test/MovementLabPSDHUD_v3'
shutil.copytree(B,S,dirs_exist_ok=True)
sys.path.insert(0,str(R/'tools'));from build_hud_icon_textures import paa
p=PSDImage.open(B/'ImageSources/PSD/Untitled-2.psd')
for l in p.descendants():l.visible=True
ls=list(p.descendants());out=S/'ImageSources/PSD'
rows=[(25,i+1) for i in range(4)]+[(31,0)]+[(33,i+1) for i in range(4)]+[(1,0),(23,0),(3,1),(3,2),(7,1),(7,2),(11,0),(31,0),(13,1),(13,2),(17,1),(17,2),(17,3),(21,0),(13,3),(45,0),(43,0),(41,0)]
# Original PSD coordinate system keeps body position independent of projecting rifle.
# Torso midpoint measured in the supplied layer art (not full rifle bounding box).
centres={1:202,3:202,7:202,11:202,25:202,31:202,23:202,13:213,17:204,21:205,33:202,41:202,45:202,43:202}
report=[]
for n,(li,count) in enumerate(rows):
 a=ls[li].composite(force=True).convert('RGBA');a.save(out/f'layer_{li}.png')
 canvas=Image.new('RGBA',(600,330))
 x=210+ls[li].left-centres[li];y=320-a.height
 canvas.paste(a,(x,y)) # preserve native source pixels; no pre-downsampling
 if count:
  bars=ls[{1:26,2:27,3:28,4:29}[count]].composite(force=True).convert('RGBA')
  canvas.paste(bars,(450+(140-bars.width)//2,320-bars.height))
 canvas=canvas.resize((931,512),Image.Resampling.LANCZOS)
 fitted=Image.new('RGBA',(1024,512));fitted.paste(canvas,(46,0));canvas=fitted
 png=out/f'icon_{n:02}.png';canvas.save(png);paa(png,S/f'StartGateSource/GUI/Textures/icon_{n:02}.paa')
 report.append({'icon':n,'layer':ls[li].name,'original_size':a.size,'torso_centre':centres[li],'placement':[x,y],'level_lines':count})
(out/'export-v3.json').write_text(json.dumps(report,indent=2))
f=S/'StartGateSource/Scripts/5_Mission/MovementLabSpeedHUD.c';t=f.read_text().replace('int expectedWidth = 512','int expectedWidth = 1024').replace('textureHeight != 256','textureHeight != 512');f.write_text(t)
# Keep exactly v2 display size, positioning, selection and movement.
assert 'SetSize(140, 70)' in t and 'speedW - 140, speedY - 76' in t
for old in (B/'StartGateSource/Scripts/4_World').glob('*'):
 if old.is_file():assert old.read_bytes()==(S/old.relative_to(B)).read_bytes()
preview=Image.new('RGB',(1120,7*170),(45,45,45));d=ImageDraw.Draw(preview)
for n in range(27):
 a=Image.open(out/f'icon_{n:02}.png');a.thumbnail((280,140));x=(n%4)*280;y=(n//4)*170;preview.paste(a,(x,y),a);d.text((x+8,y+145),str(n),fill='white')
preview.save(R/'artifacts/MovementLab_PSD_HUD_v3_Preview.png')
(S/'README-PSD-HUD.txt').write_text('PSD HUD v3: original PSD artwork exported without pre-downsampling on1024x512 PAA canvases. Aiming aligned by torso position rather than rifle bounding width. Same140x70 display and stamina anchor asv2. Speeds/controls unchanged. Native rendering needs local test.\n')
import package_movement_logic_test as pack
pack.SOURCE=S;pack.OUTPUT=R/'artifacts/MovementLab_PSD_HUD_v3.zip';pack.ARCHIVE_ROOT=S.name;pack.main()
