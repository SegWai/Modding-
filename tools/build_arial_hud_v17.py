from pathlib import Path
from PIL import Image,ImageFont,ImageDraw,ImageFilter
import sys,shutil,json
sys.dont_write_bytecode=True
R=Path('/workspace/Modding-');b=R/'hud-icons-test/MovementLabHeldItemHUD_v16';s=R/'hud-icons-test/MovementLabHeldItemHUD_v17';shutil.copytree(b,s,dirs_exist_ok=True)
sys.path.insert(0,str(R/'tools'));from build_hud_icon_textures import paa
fontpath=Path('/workspace/attachments/509398f4-bf9f-484b-b7e0-b0227747d251/ARIALBD.TTF');font=ImageFont.truetype(str(fontpath),64);assert font.getname()==('Arial','Bold')
out=s/'ImageSources/ArialBold';out.mkdir(exist_ok=True);tex=s/'StartGateSource/GUI/Textures/ArialBold';tex.mkdir(exist_ok=True)
metrics={};cases=[]
for code in range(32,127):
 ch=chr(code);mask=Image.new('L',(128,128));d=ImageDraw.Draw(mask);d.text((24,96),ch,font=font,fill=255,anchor='ls')
 shadow=mask.filter(ImageFilter.GaussianBlur(6));shadow=shadow.point(lambda a:round(a*.8))
 canvas=Image.new('RGBA',(128,128));black=Image.new('RGBA',(128,128),(0,0,0,0));black.putalpha(shadow);canvas.alpha_composite(black)
 white=Image.new('RGBA',(128,128),(255,255,255,0));white.putalpha(mask);canvas.alpha_composite(white)
 png=out/f'glyph_{code}.png';canvas.save(png);paa(png,tex/f'glyph_{code}.paa')
 advance=font.getlength(ch);metrics[str(code)]=advance;cases.append(f'            case {code}: return {advance:.6f};')
(out/'font-info.json').write_text(json.dumps({'source_font':fontpath.name,'family':font.getname(),'source_size':64,'glyph_canvas':[128,128],'label_points':2.5,'reference_dpi':300,'reference_pixel_size':2.5*300/72,'metrics':metrics},indent=2))
# Preserve original source locally, but no TTF distribution needed: glyph assets are used at runtime.
code='''// Bitmap glyphs rendered from supplied Arial Bold; dynamic labels, no native-font substitution.
class MovementLabArialLine
{
    protected Widget m_Root;
    protected ref array<ImageWidget> m_Glyphs = new array<ImageWidget>();
    protected ref array<int> m_Codes = new array<int>();

    protected float Advance(int code)
    {
        switch (code)
        {
'''+ '\n'.join(cases)+'''
        }
        return 39.09375;
    }

    void Update(TextWidget nativeLabel, bool visible, float fontPixels)
    {
        if (!nativeLabel)
            return;
        float x;
        float y;
        float w;
        float h;
        nativeLabel.GetPos(x, y);
        nativeLabel.GetSize(w, h);
        int flags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
        if (!m_Root)
            m_Root = GetGame().GetWorkspace().CreateWidget(FrameWidgetTypeID, x, y, w, h, flags, 0xFFFFFFFF, 3, nativeLabel.GetParent());
        if (!m_Root)
            return;
        m_Root.SetPos(x, y);
        m_Root.SetSize(w, h);
        m_Root.Show(visible);
        if (!visible)
        {
            nativeLabel.Show(false);
            return;
        }
        string label;
        nativeLabel.GetText(label);
        float scale = fontPixels / 64;
        float cursor = 0;
        int used = 0;
        for (int letterIndex = 0; letterIndex < label.Length(); letterIndex++)
        {
            int glyphCode = label.Get(letterIndex).ToAscii();
            if (glyphCode < 32 || glyphCode > 126)
                glyphCode = 63;
            float letterAdvance = Advance(glyphCode) * scale;
            if (cursor + letterAdvance > w)
                break;
            ImageWidget glyph;
            if (used < m_Glyphs.Count())
                glyph = m_Glyphs[used];
            else
            {
                glyph = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 128 * scale, 128 * scale, flags | WidgetFlags.STRETCH | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND, 0xFFFFFFFF, 0, m_Root));
                if (!glyph)
                    return;
                m_Glyphs.Insert(glyph);
                m_Codes.Insert(-1);
            }
            if (m_Codes[used] != glyphCode)
            {
                bool loaded = glyph.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/ArialBold/glyph_" + glyphCode + ".paa");
                if (!loaded)
                {
                    m_Root.Show(false);
                    nativeLabel.Show(true);
                    return;
                }
                glyph.SetImage(0);
                m_Codes[used] = glyphCode;
            }
            glyph.SetPos(cursor - 24 * scale, fontPixels - 96 * scale);
            glyph.SetSize(128 * scale, 128 * scale);
            glyph.Show(true);
            cursor = cursor + letterAdvance;
            used = used + 1;
        }
        for (int spareIndex = used; spareIndex < m_Glyphs.Count(); spareIndex++)
            m_Glyphs[spareIndex].Show(false);
        nativeLabel.Show(false);
    }
}
'''
(s/'StartGateSource/Scripts/5_Mission/MovementLabArialLine.c').write_text(code)
f=s/'StartGateSource/Scripts/5_Mission/MovementLabHeldItemCard.c';t=f.read_text();t=t.replace('    protected Widget m_Root;','''    protected Widget m_Root;
    protected ref MovementLabArialLine m_ArialTitle = new MovementLabArialLine();
    protected ref MovementLabArialLine m_ArialCalibre = new MovementLabArialLine();
    protected ref MovementLabArialLine m_ArialMode = new MovementLabArialLine();
    protected ref MovementLabArialLine m_ArialRounds = new MovementLabArialLine();''')
# Render after live field values and visibility are updated.
needle='''        MovementLabUpdateCard(m_Root, m_Root, item);''';assert needle in t
t=t.replace(needle,needle+'''
        // 2.5pt at Photoshop300dpi reference; screen scaling follows card height.
        float fontPixels = 10.416667 * height / 66;
        m_ArialTitle.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardName")), true, fontPixels);
        m_ArialCalibre.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardCalibre")), Weapon.Cast(item) != null, fontPixels);
        m_ArialMode.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardMode")), Weapon.Cast(item) != null, fontPixels);
        m_ArialRounds.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardRounds")), Weapon.Cast(item) != null, fontPixels);''')
# Unicode ellipsis becomes ASCII in font renderer.
t=t.replace('+ "…"','+ "."');f.write_text(t)
(s/'README-Held-Item-HUD.txt').write_text('v17: actual supplied Arial Bold rendered into95 bitmap glyph resources, dynamic names/calibres/count/mode. Labels2.5pt interpreted at300dpi reference=10.4167screen pixels at708p, scales withcard. Font shadow baked black80% blur6sourcepixels. Native fallback ifglyph unavailable. Background original alpha still pending: inline image has no accessible file pointer, unchangedflat placeholder. Live object1pxoutline remains unresolved. +5% glyph HUD/+2% stamina retained. Native compile/visual check required.\n')
import package_movement_logic_test as pack
pack.SOURCE=s;pack.OUTPUT=R/'artifacts/MovementLab_Held_Item_Arial_v17.zip';pack.ARCHIVE_ROOT=s.name;pack.main()
print('Arial Bold glyphs generated:',len(metrics),'Background unchanged;300dpi sizing assumption documented.')
