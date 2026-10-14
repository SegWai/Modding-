from pathlib import Path
import sys,shutil,re,json,io,zipfile
from PIL import Image,ImageDraw
import vtracer,cairosvg
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[1];B=R/'hud-icons-test/MovementLabPSDHUD_v3';S=R/'hud-icons-test/MovementLabPSDHUD_v4';shutil.copytree(B,S,dirs_exist_ok=True)
sys.path.insert(0,str(R/'tools'));from build_hud_icon_textures import paa
out=S/'ImageSources/PSD';vec=S/'ImageSources/Vectors';vec.mkdir(exist_ok=True)
rows=[(25,i+1) for i in range(4)]+[(31,0)]+[(33,i+1) for i in range(4)]+[(1,0),(23,0),(3,1),(3,2),(7,1),(7,2),(11,0),(31,0),(13,1),(13,2),(17,1),(17,2),(17,3),(21,0),(13,3),(45,0),(43,0),(41,0)]
centres={1:202,3:202,7:202,11:202,25:202,31:202,23:202,13:213,17:204,21:205,33:202,41:202,45:202,43:202}
from psd_tools import PSDImage
p=PSDImage.open(out/'Untitled-2.psd');ls=list(p.descendants())
checks={}
for li in sorted(set(x[0] for x in rows)|{26,27,28,29}):
 a=Image.open(out/f'layer_{li}.png') if (out/f'layer_{li}.png').exists() else None
 if a is None:
  for l in p.descendants():l.visible=True
  a=ls[li].composite(force=True).convert('RGBA')
 mask=a.getchannel('A').point(lambda x:0 if x>=128 else 255);tmp=Path('/tmp/ml-vector-mask.png');mask.save(tmp)
 svg=vec/f'layer_{li}.svg'
 vtracer.convert_image_to_svg_py(str(tmp),str(svg),colormode='binary',mode='spline',filter_speckle=1,corner_threshold=60,length_threshold=1,path_precision=3)
 text=svg.read_text().replace('fill="#000000"','fill="#FFFFFF"');svg.write_text(text)
 rendered=Image.open(io.BytesIO(cairosvg.svg2png(url=str(svg)))).convert('RGBA').getchannel('A')
 src=a.getchannel('A');sa=list(src.getdata());ra=list(rendered.getdata());intersection=sum(x>=128 and y>=128 for x,y in zip(sa,ra));union=sum(x>=128 or y>=128 for x,y in zip(sa,ra));iou=intersection/union
 assert iou>.94,(li,iou)
 checks[str(li)]=iou
for n,(li,count) in enumerate(rows):
 a=Image.open(out/f'layer_{li}.png');body=re.search(r'<svg[^>]*>(.*)</svg>',(vec/f'layer_{li}.svg').read_text(),re.S).group(1)
 x=210+ls[li].left-centres[li];y=320-a.height
 content=f'<g transform="translate({x},{y})">{body}</g>'
 if count:
  bi={1:26,2:27,3:28,4:29}[count];bar=re.search(r'<svg[^>]*>(.*)</svg>',(vec/f'layer_{bi}.svg').read_text(),re.S).group(1);bw=ls[bi].width;bh=ls[bi].height
  content+=f'<g transform="translate({450+(140-bw)//2},{320-bh})">{bar}</g>'
 svg=vec/f'icon_{n:02}.svg';svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="512" viewBox="0 0 600 330">{content}</svg>')
 # Render vectors at4x, downsample once to high-resolution native texture.
 png=out/f'icon_{n:02}.png';render=cairosvg.svg2png(url=str(svg),output_width=4096,output_height=2048);Image.open(io.BytesIO(render)).resize((1024,512),Image.Resampling.LANCZOS).save(png);paa(png,S/f'StartGateSource/GUI/Textures/icon_{n:02}.paa')
(vec/'trace-validation.json').write_text(json.dumps(checks,indent=2))
f=S/'StartGateSource/Scripts/5_Mission/MovementLabSpeedHUD.c';t=f.read_text()
needle='        m_MovementLabSpeedRoot.SetScreenPos(speedX + speedW - 140, speedY - 76);'
t=t.replace(needle,needle+'''
        // Preserve native noise visibility logic; rotate/reposition its existing bars.
        if (m_Presence)
        {
            m_Presence.SetScreenPos(speedX + speedW + 8, speedY - 34);
            m_Presence.SetScreenSize(18, 40);
            MovementLabPositionNoiseBar(m_PresenceLevel0, 0, speedX + speedW + 8, speedY);
            MovementLabPositionNoiseBar(m_PresenceLevel1, 1, speedX + speedW + 8, speedY);
            MovementLabPositionNoiseBar(m_PresenceLevel2, 2, speedX + speedW + 8, speedY);
            MovementLabPositionNoiseBar(m_PresenceLevel3, 3, speedX + speedW + 8, speedY);
            MovementLabPositionNoiseBar(m_PresenceLevel4, 4, speedX + speedW + 8, speedY);
        }''')
pos=t.rfind('\n}')
t=t[:pos]+'''
    protected void MovementLabPositionNoiseBar(Widget bar, int index, float x, float y)
    {
        if (!bar)
            return;
        bar.SetScreenSize(5, 16);
        bar.SetRotation(0, 0, 90);
        bar.SetScreenPos(x, y - 6 - index * 7);
    }

    Widget MovementLabGetStaminaAnchor()
    {
        if (!m_Stamina)
            return null;
        return m_Stamina.GetParent();
    }
'''+t[pos:];f.write_text(t)
(S/'StartGateSource/Scripts/5_Mission/MovementLabItemHUD.c').write_text('''// Move only the equipped-item display; keep interaction prompts native.
modded class ItemActionsWidget
{
    override protected void Update()
    {
        super.Update();
        if (!m_Hud || !m_ItemLeft || !MovementLabStartGate.Enabled)
            return;
        Widget staminaAnchor = m_Hud.MovementLabGetStaminaAnchor();
        if (!staminaAnchor)
            return;
        float anchorX;
        float anchorY;
        float anchorW;
        float anchorH;
        staminaAnchor.GetScreenPos(anchorX, anchorY);
        staminaAnchor.GetScreenSize(anchorW, anchorH);
        m_ItemLeft.SetScreenPos(anchorX, anchorY + anchorH + 6);
    }
}
''')
preview=Image.new('RGB',(1120,7*170),(45,45,45))
for n in range(27):
 a=Image.open(out/f'icon_{n:02}.png');a.thumbnail((280,140));preview.paste(a,((n%4)*280,(n//4)*170),a)
preview.save(R/'artifacts/MovementLab_Vector_HUD_Preview.png')
(S/'README-PSD-HUD.txt').write_text('PSD HUD v4. Silhouette SVG curves traced from user PSD; raster shape overlap >94% validated. Vector rendered at4x then1024x512 native PAA. Display remains140x70. Native sound bars right of stamina and bottom-to-top. Equipped-item panel below stamina, native action prompts retained. Native render/compile/layout need local DayZ test. No movement changes.\n')
import package_movement_logic_test as pack
pack.SOURCE=S;pack.OUTPUT=R/'artifacts/MovementLab_PSD_HUD_v4.zip';pack.ARCHIVE_ROOT=S.name;pack.main()
with zipfile.ZipFile(R/'artifacts/MovementLab_Indicator_Vectors.zip','w',zipfile.ZIP_DEFLATED) as z:
 for file in vec.glob('*.svg'):z.write(file,file.name)
print('Trace minimum overlap',min(checks.values()))
