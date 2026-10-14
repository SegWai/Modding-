// Bitmap glyphs rendered from supplied Arial Bold; dynamic labels, no native-font substitution.
class MovementLabArialLine
{
    protected Widget m_Root;
    protected ref array<ImageWidget> m_Glyphs = new array<ImageWidget>();
    protected ref array<int> m_Codes = new array<int>();

    protected float Advance(int code)
    {
        switch (code)
        {
            case 32: return 17.781250;
            case 33: return 21.312500;
            case 34: return 30.343750;
            case 35: return 35.593750;
            case 36: return 35.593750;
            case 37: return 56.906250;
            case 38: return 46.218750;
            case 39: return 15.218750;
            case 40: return 21.312500;
            case 41: return 21.312500;
            case 42: return 24.906250;
            case 43: return 37.375000;
            case 44: return 17.781250;
            case 45: return 21.312500;
            case 46: return 17.781250;
            case 47: return 17.781250;
            case 48: return 35.593750;
            case 49: return 35.593750;
            case 50: return 35.593750;
            case 51: return 35.593750;
            case 52: return 35.593750;
            case 53: return 35.593750;
            case 54: return 35.593750;
            case 55: return 35.593750;
            case 56: return 35.593750;
            case 57: return 35.593750;
            case 58: return 21.312500;
            case 59: return 21.312500;
            case 60: return 37.375000;
            case 61: return 37.375000;
            case 62: return 37.375000;
            case 63: return 39.093750;
            case 64: return 62.406250;
            case 65: return 46.218750;
            case 66: return 46.218750;
            case 67: return 46.218750;
            case 68: return 46.218750;
            case 69: return 42.687500;
            case 70: return 39.093750;
            case 71: return 49.781250;
            case 72: return 46.218750;
            case 73: return 17.781250;
            case 74: return 35.593750;
            case 75: return 46.218750;
            case 76: return 39.093750;
            case 77: return 53.312500;
            case 78: return 46.218750;
            case 79: return 49.781250;
            case 80: return 42.687500;
            case 81: return 49.781250;
            case 82: return 46.218750;
            case 83: return 42.687500;
            case 84: return 39.093750;
            case 85: return 46.218750;
            case 86: return 42.687500;
            case 87: return 60.406250;
            case 88: return 42.687500;
            case 89: return 42.687500;
            case 90: return 39.093750;
            case 91: return 21.312500;
            case 92: return 17.781250;
            case 93: return 21.312500;
            case 94: return 37.375000;
            case 95: return 35.593750;
            case 96: return 21.312500;
            case 97: return 35.593750;
            case 98: return 39.093750;
            case 99: return 35.593750;
            case 100: return 39.093750;
            case 101: return 35.593750;
            case 102: return 21.312500;
            case 103: return 39.093750;
            case 104: return 39.093750;
            case 105: return 17.781250;
            case 106: return 17.781250;
            case 107: return 35.593750;
            case 108: return 17.781250;
            case 109: return 56.906250;
            case 110: return 39.093750;
            case 111: return 39.093750;
            case 112: return 39.093750;
            case 113: return 39.093750;
            case 114: return 24.906250;
            case 115: return 35.593750;
            case 116: return 21.312500;
            case 117: return 39.093750;
            case 118: return 35.593750;
            case 119: return 49.781250;
            case 120: return 35.593750;
            case 121: return 35.593750;
            case 122: return 32.000000;
            case 123: return 24.906250;
            case 124: return 17.906250;
            case 125: return 24.906250;
            case 126: return 37.375000;
        }
        return 39.09375;
    }

    void Update(TextWidget nativeLabel, string label, bool visible, float fontPixels)
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
            glyph.ClearFlags(WidgetFlags.NOFILTER);
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
