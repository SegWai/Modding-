// Image-based stance/speed indicator. Reads selection; never controls movement.
modded class IngameHud
{
    protected bool m_MovementLabSpeedReady;
    protected Widget m_MovementLabSpeedRoot;
    protected ImageWidget m_MovementLabSpeedImage;
    protected TextWidget m_MovementLabSpeedLabel;
    protected int m_MovementLabLastIcon = -1;

    override void Init(Widget hud_panel_widget)
    {
        super.Init(hud_panel_widget);
        m_MovementLabSpeedReady = false;
        m_MovementLabLastIcon = -1;
        WidgetFlags iconFlags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS;
        iconFlags = iconFlags | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE;
        iconFlags = iconFlags | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
        m_MovementLabSpeedRoot = hud_panel_widget.FindAnyWidget("MovementLabSpeedIndicator");
        if (!m_MovementLabSpeedRoot)
        {
            m_MovementLabSpeedRoot = GetGame().GetWorkspace().CreateWidget(FrameWidgetTypeID, 0, 0, 132, 104, iconFlags, 0xFFFFFFFF, 20, hud_panel_widget);
            if (!m_MovementLabSpeedRoot)
                return;
            m_MovementLabSpeedRoot.SetName("MovementLabSpeedIndicator");
        }
        m_MovementLabSpeedRoot.Show(false);
        m_MovementLabSpeedImage = ImageWidget.Cast(m_MovementLabSpeedRoot.FindAnyWidget("MovementLabSpeedImage"));
        if (!m_MovementLabSpeedImage)
        {
            m_MovementLabSpeedImage = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 88, 80, iconFlags | WidgetFlags.CUSTOMUV | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND, 0xFFFFFFFF, 0, m_MovementLabSpeedRoot));
            if (m_MovementLabSpeedImage)
                m_MovementLabSpeedImage.SetName("MovementLabSpeedImage");
        }
        m_MovementLabSpeedLabel = TextWidget.Cast(m_MovementLabSpeedRoot.FindAnyWidget("MovementLabSpeedLabel"));
        if (!m_MovementLabSpeedLabel)
        {
            m_MovementLabSpeedLabel = TextWidget.Cast(GetGame().GetWorkspace().CreateWidget(TextWidgetTypeID, 0, 84, 132, 18, iconFlags, 0xFFFFFFFF, 0, m_MovementLabSpeedRoot));
            if (m_MovementLabSpeedLabel)
            {
                m_MovementLabSpeedLabel.SetName("MovementLabSpeedLabel");
                m_MovementLabSpeedLabel.SetTextExactSize(12);
                m_MovementLabSpeedLabel.SetOutline(1);
            }
        }
        if (!m_MovementLabSpeedImage || !m_MovementLabSpeedLabel)
            return;
        bool atlasLoaded = m_MovementLabSpeedImage.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/stance-atlas.paa");
        bool extraLoaded = m_MovementLabSpeedImage.LoadImageFile(1, "MovementLabStartGate/GUI/Textures/slow-aim-level-3.paa");
        if (!atlasLoaded || !extraLoaded)
        {
            Print("[MovementLab HUD Icons] Texture load failed; indicator hidden.");
            return;
        }
        int atlasWidth;
        int atlasHeight;
        int extraWidth;
        int extraHeight;
        m_MovementLabSpeedImage.GetImageSize(0, atlasWidth, atlasHeight);
        m_MovementLabSpeedImage.GetImageSize(1, extraWidth, extraHeight);
        if (atlasWidth != 2048 || atlasHeight != 1024 || extraWidth != 2048 || extraHeight != 2048)
        {
            Print("[MovementLab HUD Icons] Unexpected texture dimensions; indicator hidden.");
            return;
        }
        m_MovementLabSpeedReady = true;
        Print("[MovementLab HUD Icons] 24 stance/level images ready.");
    }

    protected bool MovementLabSetIconUV(int icon)
    {
        float x0;
        float y0;
        float x1;
        float y1;
        switch (icon)
        {
            case 0: x0 = 0.023925781; y0 = 0.126953125; x1 = 0.102050781; y1 = 0.270507812; break;
            case 1: x0 = 0.109375000; y0 = 0.126953125; x1 = 0.189941406; y1 = 0.270507812; break;
            case 2: x0 = 0.197265625; y0 = 0.126953125; x1 = 0.277343750; y1 = 0.270507812; break;
            case 3: x0 = 0.285156250; y0 = 0.126953125; x1 = 0.364746094; y1 = 0.270507812; break;
            case 4: x0 = 0.374023438; y0 = 0.126953125; x1 = 0.459960938; y1 = 0.270507812; break;
            case 5: x0 = 0.483886719; y0 = 0.126953125; x1 = 0.559570312; y1 = 0.270507812; break;
            case 6: x0 = 0.567382812; y0 = 0.126953125; x1 = 0.640625000; y1 = 0.270507812; break;
            case 7: x0 = 0.648437500; y0 = 0.126953125; x1 = 0.723632812; y1 = 0.270507812; break;
            case 8: x0 = 0.730957031; y0 = 0.126953125; x1 = 0.808105469; y1 = 0.270507812; break;
            case 9: x0 = 0.023925781; y0 = 0.372070312; x1 = 0.093261719; y1 = 0.535156250; break;
            case 10: x0 = 0.101074219; y0 = 0.372070312; x1 = 0.171386719; y1 = 0.535156250; break;
            case 11: x0 = 0.189941406; y0 = 0.372070312; x1 = 0.266601562; y1 = 0.535156250; break;
            case 12: x0 = 0.274902344; y0 = 0.372070312; x1 = 0.348144531; y1 = 0.535156250; break;
            case 13: x0 = 0.359863281; y0 = 0.372070312; x1 = 0.437011719; y1 = 0.535156250; break;
            case 14: x0 = 0.447265625; y0 = 0.372070312; x1 = 0.514648438; y1 = 0.535156250; break;
            case 15: x0 = 0.530761719; y0 = 0.372070312; x1 = 0.613769531; y1 = 0.535156250; break;
            case 16: x0 = 0.633789062; y0 = 0.372070312; x1 = 0.804687500; y1 = 0.535156250; break;
            case 17: x0 = 0.026367188; y0 = 0.644531250; x1 = 0.114746094; y1 = 0.812500000; break;
            case 18: x0 = 0.123046875; y0 = 0.644531250; x1 = 0.212402344; y1 = 0.812500000; break;
            case 19: x0 = 0.233398438; y0 = 0.644531250; x1 = 0.322265625; y1 = 0.812500000; break;
            case 20: x0 = 0.332031250; y0 = 0.644531250; x1 = 0.425292969; y1 = 0.812500000; break;
            case 21: x0 = 0.436035156; y0 = 0.644531250; x1 = 0.534667969; y1 = 0.812500000; break;
            case 22: x0 = 0.556152344; y0 = 0.641601562; x1 = 0.805175781; y1 = 0.817382812; break;
            case 23: x0 = 0.000000000; y0 = 0.000000000; x1 = 0.612304688; y1 = 0.612304688; break;
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

    override void Update(float timeslice)
    {
        super.Update(timeslice);
        if (!m_MovementLabSpeedRoot)
            return;
        PlayerBase speedPlayer = PlayerBase.Cast(GetGame().GetPlayer());
        bool speedVisible = m_MovementLabSpeedReady && MovementLabStartGate.Enabled && speedPlayer && speedPlayer.IsAlive() && !speedPlayer.IsUnconscious();
        if (!m_Presence || !m_Presence.IsVisibleHierarchy())
            speedVisible = false;
        m_MovementLabSpeedRoot.Show(speedVisible);
        if (!speedVisible)
            return;
        int speedIcon;
        int speedLevel;
        string speedMode;
        bool speedAuto;
        speedPlayer.MovementLabGetHUDIcon(speedIcon, speedLevel, speedMode, speedAuto);
        if (speedIcon < 0 || speedIcon > 23)
        {
            m_MovementLabSpeedRoot.Show(false);
            return;
        }
        if (speedIcon != m_MovementLabLastIcon)
        {
            int atlasSlot = 0;
            if (speedIcon == 23)
                atlasSlot = 1;
            if (!m_MovementLabSpeedImage.SetImage(atlasSlot) || !MovementLabSetIconUV(speedIcon))
            {
                m_MovementLabSpeedRoot.Show(false);
                return;
            }
            m_MovementLabLastIcon = speedIcon;
        }
        string speedLabel = speedMode;
        if (speedLevel > 0)
            speedLabel = speedLabel + " L" + speedLevel;
        int speedLabelColor = ARGB(255, 255, 255, 255);
        if (speedAuto)
        {
            speedLabel = speedLabel + " AUTO";
            speedLabelColor = ARGB(255, 235, 193, 100);
        }
        m_MovementLabSpeedLabel.SetColor(speedLabelColor);
        m_MovementLabSpeedLabel.SetText(speedLabel);
        float speedX;
        float speedY;
        float speedW;
        float speedH;
        m_Presence.GetScreenPos(speedX, speedY);
        m_Presence.GetScreenSize(speedW, speedH);
        float speedRight = speedX + speedW;
        Widget speedStance = m_HudPanelWidget.FindAnyWidget("StancePanel");
        if (speedStance)
        {
            float stanceX;
            float stanceY;
            float stanceW;
            float stanceH;
            speedStance.GetScreenPos(stanceX, stanceY);
            speedStance.GetScreenSize(stanceW, stanceH);
            speedRight = Math.Max(speedRight, stanceX + stanceW);
        }
        float viewW;
        float viewH;
        m_HudPanelWidget.GetScreenSize(viewW, viewH);
        float maxSpeedX = Math.Max(0, viewW - 132);
        float maxSpeedY = Math.Max(0, viewH - 104);
        float panelSpeedX = Math.Clamp(speedRight + 12, 0, maxSpeedX);
        float panelSpeedY = Math.Clamp(speedY, 0, maxSpeedY);
        m_MovementLabSpeedRoot.SetScreenPos(panelSpeedX, panelSpeedY);
    }
}
