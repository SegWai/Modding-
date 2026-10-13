"""Encode approved images as native PAA atlases and emit HUD UV rectangles.

No silhouettes are redrawn/cropped. Source pixels are retained at original
resolution on a power-of-two canvas. The HUD selects tiles using native UVs.
Mipmaps and BC3 compression are texture packaging, not new image artwork.
"""
from pathlib import Path
from PIL import Image, ImageStat
import io, struct, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'hud-icons-test/MovementLabHUDIcons_v1'
TEXTURES=SOURCE/'StartGateSource/GUI/Textures'

def paa(source, target):
    image=Image.open(source).convert('RGBA')
    w=1<<(image.width-1).bit_length(); h=1<<(image.height-1).bit_length()
    canvas=Image.new('RGBA',(w,h));canvas.paste(image,(0,0))
    # Standard PAA DXT5, average/max tags, 16 little-endian mip offsets, palette.
    data=bytearray(struct.pack('<H',0xff05))
    for name, color in ((b'GGATCGVA',bytes(int(v) for v in ImageStat.Stat(canvas).mean)),
                        (b'GGATCXAM',bytes(v[1] for v in canvas.getextrema()))):
        data+=name+struct.pack('<I',4)+color
    data+=b'GGATSFFO'+struct.pack('<I',64)
    table=len(data);data+=b'\0'*64+b'\0\0'
    offsets=[];mip=canvas
    while mip.width>=4 and mip.height>=4:
        dds=io.BytesIO();mip.save(dds,format='DDS',pixel_format='DXT5')
        raw=dds.getvalue();assert raw[:4]==b'DDS ' and raw[84:88]==b'DXT5'
        block=raw[128:];assert len(block)==mip.width*mip.height
        offsets.append(len(data))
        data+=struct.pack('<HH',*mip.size)+len(block).to_bytes(3,'little')+block
        mip=mip.resize((mip.width//2,mip.height//2),Image.Resampling.LANCZOS)
    offsets.append(len(data));data+=b'\0'*6
    for index, offset in enumerate(offsets):struct.pack_into('<I',data,table+index*4,offset)
    target.write_bytes(data)
    return {'source_size':image.size,'texture_size':(w,h),'mip_levels':len(offsets)-1,
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}

tiles=[
 ('crouch_1',(49,130,209,277)),('crouch_2',(224,130,389,277)),
 ('crouch_3',(404,130,568,277)),('crouch_4',(584,130,747,277)),('crouch_5',(766,130,942,277)),
 ('crouch_aim_1',(991,130,1146,277)),('crouch_aim_2',(1162,130,1312,277)),
 ('crouch_aim_3',(1328,130,1482,277)),('crouch_aim_4',(1497,130,1655,277)),
 ('standing_idle',(49,381,191,548)),('crouch_idle',(207,381,351,548)),
 ('walking_1',(389,381,546,548)),('walking_2',(563,381,713,548)),
 ('jogging_1',(737,381,895,548)),('jogging_2',(916,381,1054,548)),
 ('sprinting',(1087,381,1257,548)),('crouch_momentum',(1298,381,1648,548)),
 ('slow_aim_1',(54,660,235,832)),('slow_aim_2',(252,660,435,832)),
 ('fast_aim_1',(478,660,660,832)),('fast_aim_2',(680,660,871,832)),
 ('fast_aim_3',(893,660,1095,832)),('aim_momentum',(1139,657,1649,837)),
 ('slow_aim_3',(0,0,1254,1254))]

def main():
    TEXTURES.mkdir(parents=True,exist_ok=True)
    charts=[paa(SOURCE/'ImageSources/stance-chart.png',TEXTURES/'stance-atlas.paa'),
            paa(SOURCE/'ImageSources/slow-aim-level-3.png',TEXTURES/'slow-aim-level-3.paa')]
    rows=[];cases=[]
    for index,(name,rect) in enumerate(tiles):
        atlas=1 if index==23 else 0
        width,height=charts[atlas]['texture_size'];sw,sh=charts[atlas]['source_size']
        x0,y0,x1,y1=rect
        assert 0<=x0<x1<=sw and 0<=y0<y1<=sh
        uv=[x0/width,y0/height,x1/width,y1/height]
        rows.append({'id':index,'name':name,'atlas':atlas,'rect':rect,'uv':uv})
        cases.append('            case %d: x0 = %.9f; y0 = %.9f; x1 = %.9f; y1 = %.9f; break;'%((index,)+tuple(uv)))
    function='''    protected bool MovementLabSetIconUV(int icon)
    {
        float x0;
        float y0;
        float x1;
        float y1;
        switch (icon)
        {
%s
            default: return false;
        }
        float uv[4][2];
        uv[0][0] = x0; uv[0][1] = y0;
        uv[1][0] = x1; uv[1][1] = y0;
        uv[2][0] = x1; uv[2][1] = y1;
        uv[3][0] = x0; uv[3][1] = y1;
        m_MovementLabSpeedImage.SetUV(uv);
        float atlasHeight = 1024;
        if (icon == 23)
            atlasHeight = 2048;
        float pixelWidth = (x1 - x0) * 2048;
        float pixelHeight = (y1 - y0) * atlasHeight;
        float aspect = pixelWidth / pixelHeight;
        float availableWidth = 88;
        if (icon == 16 || icon == 22)
            availableWidth = 132;
        float iconWidth = Math.Min(availableWidth, 80 * aspect);
        float iconHeight = iconWidth / aspect;
        m_MovementLabSpeedImage.SetPos(0, (80 - iconHeight) / 2);
        m_MovementLabSpeedImage.SetSize(iconWidth, iconHeight);
        return true;
    }
'''%'\n'.join(cases)
    (SOURCE/'ImageSources/icon-map.json').write_text(json.dumps({'textures':charts,'icons':rows},indent=2)+'\n')
    (SOURCE/'ImageSources/generated-uv-method.txt').write_text(function)
    print('Encoded two native PAA textures; 24 icon UV selections; source artwork retained.')

if __name__=='__main__':main()
