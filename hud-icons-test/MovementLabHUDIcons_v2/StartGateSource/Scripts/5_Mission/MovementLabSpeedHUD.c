// Image-based stance/speed indicator. Reads selection; never controls movement.
modded class IngameHud
{
    protected bool m_MovementLabSpeedReady;
    protected Widget m_MovementLabSpeedRoot;
    protected ref array<ImageWidget> m_MovementLabSpeedImages = new array<ImageWidget>();
    protected TextWidget m_MovementLabSpeedLabel;
    protected int m_MovementLabLastIcon = -1;

    override void Init(Widget hud_panel_widget)
    {
        super.Init(hud_panel_widget);
        m_MovementLabSpeedReady = false;
        m_MovementLabLastIcon = -1;
        m_MovementLabSpeedImages.Clear();
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
        if (!m_MovementLabSpeedLabel)
            return;
        for (int iconIndex = 0; iconIndex < 24; iconIndex++)
        {
            string imageName = "MovementLabSpeedImage" + iconIndex;
            ImageWidget speedImage = ImageWidget.Cast(m_MovementLabSpeedRoot.FindAnyWidget(imageName));
            if (!speedImage)
            {
                speedImage = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 80, 80, iconFlags | WidgetFlags.STRETCH | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND, 0xFFFFFFFF, 0, m_MovementLabSpeedRoot));
                if (!speedImage)
                    return;
                speedImage.SetName(imageName);
            }
            speedImage.Show(false);
            speedImage.SetPos(0, 0);
            speedImage.SetSize(80, 80);
            int expectedWidth = 256;
            if (iconIndex == 16 || iconIndex == 22)
            {
                expectedWidth = 512;
                speedImage.SetPos(0, 7);
                speedImage.SetSize(132, 66);
            }
            string iconNumber = "" + iconIndex;
            if (iconIndex < 10)
                iconNumber = "0" + iconNumber;
            string texturePath = "MovementLabStartGate/GUI/Textures/icon_" + iconNumber + ".paa";
            bool textureLoaded = speedImage.LoadImageFile(0, texturePath);
            if (!textureLoaded || !speedImage.SetImage(0))
            {
                Print("[MovementLab HUD Icons v2] Could not load " + texturePath);
                return;
            }
            int textureWidth;
            int textureHeight;
            speedImage.GetImageSize(0, textureWidth, textureHeight);
            if (textureWidth != expectedWidth || textureHeight != 256)
            {
                Print("[MovementLab HUD Icons v2] Unexpected dimensions for " + texturePath);
                return;
            }
            m_MovementLabSpeedImages.Insert(speedImage);
        }
        m_MovementLabSpeedReady = m_MovementLabSpeedImages.Count() == 24;
        Print("[MovementLab HUD Icons v2] Individual textures ready=" + m_MovementLabSpeedReady);
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
            if (m_MovementLabLastIcon >= 0 && m_MovementLabLastIcon < m_MovementLabSpeedImages.Count())
                m_MovementLabSpeedImages[m_MovementLabLastIcon].Show(false);
            m_MovementLabSpeedImages[speedIcon].Show(true);
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
