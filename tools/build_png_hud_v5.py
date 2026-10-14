from pathlib import Path
import shutil,sys,zipfile
from PIL import Image
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];B=R/'hud-icons-test/MovementLabPSDHUD_v4';S=R/'hud-icons-test/MovementLabPNG_HUD_v5';shutil.copytree(B,S,dirs_exist_ok=True)
sys.path.insert(0,str(R/'tools'));from build_hud_icon_textures import paa
src=Path('/tmp/indicators-upload/Indicators');original=S/'ImageSources/OriginalPNGs';original.mkdir(exist_ok=True)
for p in src.glob('*.png'):shutil.copyfile(p,original/p.name)
rows=[('crouch walk',n+1) for n in range(4)]+[('crouch jog',0)]+[('crouch aim walk',n+1) for n in range(4)]+[('stationary',0),('crouch stationary',0),('walk',1),('walk',2),('jogging',1),('jogging',2),('spriting',0),('crouch jog',0),('walking aim',1),('walking aim',2),('jog aim',1),('jog aim',2),('jog aim',3),('momentum',0),('walking aim',3),('prone',0),('prone aim',0),('crouch aim stationary',0)]
centres={'walking aim':213,'jog aim':204,'momentum':205}
for n,(name,level) in enumerate(rows):
 a=Image.open(original/(name+'.png')).convert('RGBA');bbox=a.getbbox();tile=a.crop(bbox)
 canvas=Image.new('RGBA',(600,330));canvas.paste(tile,(210+bbox[0]-centres.get(name,202),320-tile.height))
 if level:
  marks=Image.open(B/f'ImageSources/PSD/layer_{ {1:26,2:27,3:28,4:29}[level] }.png') if (B/f'ImageSources/PSD/layer_{ {1:26,2:27,3:28,4:29}[level] }.png').exists() else None
  if marks is None:
   from psd_tools import PSDImage
   psd=PSDImage.open(B/'ImageSources/PSD/Untitled-2.psd')
   for l in psd.descendants():l.visible=True
   marks=list(psd.descendants())[{1:26,2:27,3:28,4:29}[level]].composite(force=True)
  canvas.paste(marks,(450+(140-marks.width)//2,320-marks.height))
 # One high-resolution render; no vector redraw or source reduction.
 canvas=canvas.resize((931,512),Image.Resampling.LANCZOS);fitted=Image.new('RGBA',(1024,512));fitted.paste(canvas,(46,0))
 png=S/f'ImageSources/PSD/icon_{n:02}.png';fitted.save(png);paa(png,S/f'StartGateSource/GUI/Textures/icon_{n:02}.paa')
for p in original.glob('*.png'):assert p.read_bytes()==(src/p.name).read_bytes()
(S/'README-PSD-HUD.txt').write_text('PNG HUD v5 uses uploaded Indicators.rar originals directly, not vector replacements. Original PNG files preserved byte-for-byte in ImageSources/OriginalPNGs. Same140x70 display and torso centring, weapon panel below stamina and sound bars on right increasing upwards. Original PSD line marks retained. Native PAA texture conversion and display downsampling still apply; native sharpness/positioning needs local test. No gameplay changes.\n')
import package_movement_logic_test as p
p.SOURCE=S;p.OUTPUT=R/'artifacts/MovementLab_PNG_HUD_v5.zip';p.ARCHIVE_ROOT=S.name;p.main()
for old in (B/'StartGateSource/Scripts').rglob('*.c'):assert old.read_bytes()==(S/old.relative_to(B)).read_bytes()
print('14 uploaded original PNGs verified byte-identical; HUD and gameplay scripts unchanged.')
