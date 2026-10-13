"""Extract approved chart tiles for texture packaging; no artwork redesign.

Each tile is fitted without stretching onto a power-of-two PAA canvas, removing
the need for DayZ's incompatible multidimensional SetUV interface.
"""
from pathlib import Path
from PIL import Image
import json, tempfile, sys
sys.dont_write_bytecode=True
from build_hud_icon_textures import paa
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'hud-icons-test/MovementLabHUDIcons_v2'
TEXTURES=SOURCE/'StartGateSource/GUI/Textures'

def main():
    manifest=json.loads((SOURCE/'ImageSources/icon-map.json').read_text())
    images=[Image.open(SOURCE/'ImageSources/stance-chart.png').convert('RGBA'),
            Image.open(SOURCE/'ImageSources/slow-aim-level-3.png').convert('RGBA')]
    outputs=[]
    for icon in manifest['icons']:
        tile=images[icon['atlas']].crop(tuple(icon['rect']))
        size=(512,256) if icon['id'] in (16,22) else (256,256)
        scale=min(size[0]/tile.width,size[1]/tile.height)
        tile=tile.resize((round(tile.width*scale),round(tile.height*scale)),Image.Resampling.LANCZOS)
        canvas=Image.new('RGBA',size)
        canvas.paste(tile,((size[0]-tile.width)//2,(size[1]-tile.height)//2))
        name='icon_%02d.paa'%icon['id']
        with tempfile.TemporaryDirectory(prefix='movementlab-tile-') as folder:
            p=Path(folder)/'tile.png';canvas.save(p); report=paa(p,TEXTURES/name)
        outputs.append({'id':icon['id'],'name':icon['name'],'file':name,'texture_size':size,
                        'source_rect':icon['rect'],'fitted_size':tile.size,'mip_levels':report['mip_levels']})
    # In this NEW version only, remove the unused giant atlases and UV generator.
    for n in ('stance-atlas.paa','slow-aim-level-3.paa'):
        (TEXTURES/n).unlink(missing_ok=True)
    (SOURCE/'ImageSources/generated-uv-method.txt').unlink(missing_ok=True)
    (SOURCE/'ImageSources/individual-textures.json').write_text(json.dumps(outputs,indent=2)+'\n')
    print('24 individual PAA files ready; preserved tile aspect ratios; no runtime UV call.')

if __name__=='__main__':main()
