from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import shutil,sys
sys.dont_write_bytecode=True
R=Path('/workspace/Modding-');b=R/'hud-icons-test/MovementLabHeldItemHUD_v18';s=R/'hud-icons-test/MovementLabHeldItemHUD_v19';shutil.copytree(b,s,dirs_exist_ok=True)
sys.path.insert(0,str(R/'tools'));from build_hud_icon_textures import paa
font=ImageFont.truetype('/workspace/attachments/509398f4-bf9f-484b-b7e0-b0227747d251/ARIALBD.TTF',256);assert font.getname()==('Arial','Bold')
for code in range(32,127):
 mask=Image.new('L',(512,512));ImageDraw.Draw(mask).text((96,384),chr(code),font=font,fill=255,anchor='ls');mask=mask.resize((128,128),Image.Resampling.LANCZOS)
 shadow=mask.filter(ImageFilter.GaussianBlur(6)).point(lambda a:round(a*.8));canvas=Image.new('RGBA',(128,128));bg=Image.new('RGBA',(128,128),(0,0,0,0));bg.putalpha(shadow);canvas.alpha_composite(bg)
 fg=Image.new('RGBA',(128,128),(255,255,255,0));fg.putalpha(mask);canvas.alpha_composite(fg)
 png=s/f'ImageSources/ArialBold/glyph_{code}.png';canvas.save(png);paa(png,s/f'StartGateSource/GUI/Textures/ArialBold/glyph_{code}.paa')
f=s/'StartGateSource/Scripts/5_Mission/MovementLabArialLine.c';t=f.read_text().replace('            glyph.SetPos(cursor - 24 * scale, fontPixels - 96 * scale);','            glyph.ClearFlags(WidgetFlags.NOFILTER);\n            glyph.SetPos(cursor - 24 * scale, fontPixels - 96 * scale);');f.write_text(t)
f=s/'StartGateSource/Scripts/5_Mission/MovementLabHeldItemCard.c';t=f.read_text().replace('10.416667 * height / 66','8.8 * height / 66').replace('    protected ItemPreviewWidget m_Preview;','    protected ItemPreviewWidget m_Preview;\n    protected ref array<ItemPreviewWidget> m_OutlinePreviews = new array<ItemPreviewWidget>();')
t=t.replace('''        if (m_Root)
            m_Preview = ItemPreviewWidget.Cast(m_Root.FindAnyWidget("MovementLabHeldRender"));''','''        if (m_Root)
        {
            m_Preview = ItemPreviewWidget.Cast(m_Root.FindAnyWidget("MovementLabHeldRender"));
            if (m_Preview)
                m_Preview.SetSort(1);
            for (int outlineIndex = 0; outlineIndex < 4; outlineIndex++)
            {
                ItemPreviewWidget outline = ItemPreviewWidget.Cast(m_Root.FindAnyWidget("MLWeaponOutline" + outlineIndex));
                if (outline)
                {
                    outline.SetSort(0);
                    outline.SetColor(0xFF000000);
                    m_OutlinePreviews.Insert(outline);
                }
            }
        }''')
t=t.replace('''            m_Preview.SetItem(null);
            return;''','''            m_Preview.SetItem(null);
            for (int clearIndex = 0; clearIndex < m_OutlinePreviews.Count(); clearIndex++)
                m_OutlinePreviews[clearIndex].SetItem(null);
            return;''',1)
needle='''        m_Preview.SetSize(fraction, fraction);''';assert needle in t
t=t.replace(needle,needle+'''
        // Experimental1px silhouette outline: black-tinted preview passes behind the main render.
        for (int strokeIndex = 0; strokeIndex < m_OutlinePreviews.Count(); strokeIndex++)
        {
            ItemPreviewWidget strokePreview = m_OutlinePreviews[strokeIndex];
            bool strokeVisible = item.IsWeapon();
            strokePreview.Show(strokeVisible);
            if (!strokeVisible)
            {
                strokePreview.SetItem(null);
                continue;
            }
            float offsetX = 0;
            float offsetY = 0;
            if (strokeIndex == 0)
                offsetX = -1 / width;
            else if (strokeIndex == 1)
                offsetX = 1 / width;
            else if (strokeIndex == 2)
                offsetY = -1 / height;
            else
                offsetY = 1 / height;
            strokePreview.SetPos(inset + offsetX, inset + offsetY);
            strokePreview.SetSize(fraction, fraction);
            strokePreview.SetColor(0xFF000000);
            if (strokePreview.GetItem() != item)
            {
                strokePreview.SetItem(item);
                strokePreview.SetModelPosition("0 0 0");
                strokePreview.SetModelOrientation("0 0 0");
                strokePreview.SetView(item.GetViewIndex());
            }
        }''')
f.write_text(t)
f=s/'StartGateSource/GUI/MovementLabHeldItem.layout';t=f.read_text();pos=t.index('  ItemPreviewWidgetClass MovementLabHeldRender')
blocks=''
for n in range(4):blocks+=f'''  ItemPreviewWidgetClass MLWeaponOutline{n} {{
   visible 0
   ignorepointer 1
   color 0 0 0 1
   position 0.07 0.07
   size 0.86 0.86
   hexactpos 0
   vexactpos 0
   hexactsize 0
   vexactsize 0
  }}
'''
t=t[:pos]+blocks+t[pos:];f.write_text(t)
(s/'README-Held-Item-HUD.txt').write_text('v19 actual user Arial Bold still used. Glyphs supersampled4x then antialiased; texture filtering explicitly enabled; label size reduced10.4167to8.8px (~15.5%). Experimental1px live weapon outline uses4offset black-tinted previews behind main model; native tint/render support must be tested, no claim it works. Background exact alpha pending binaryPNG. Quickslots/gameplay unchanged. Native compile/visual check required.\n')
import package_movement_logic_test as p;p.SOURCE=s;p.OUTPUT=R/'artifacts/MovementLab_Held_Item_Smooth_Arial_v19.zip';p.ARCHIVE_ROOT=s.name;p.main()
print('Verified actual font family',font.getname(),'; 95 supersampled glyphs; native outline experiment unverified.')
