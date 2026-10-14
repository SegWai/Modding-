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
            m_MovementLabSpeedRoot = GetGame().GetWorkspace().CreateWidget(FrameWidgetTypeID, 0, 0, 140, 72, iconFlags, 0xFFFFFFFF, 20, hud_panel_widget);
            if (!m_MovementLabSpeedRoot)
                return;
            m_MovementLabSpeedRoot.SetName("MovementLabSpeedIndicator");
        }
        m_MovementLabSpeedRoot.Show(false);
        for (int iconIndex = 0; iconIndex < 27; iconIndex++)
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
            speedImage.SetSize(140, 70);
            int expectedWidth = 1024;
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
            if (textureWidth != expectedWidth || textureHeight != 512)
            {
                Print("[MovementLab HUD Icons v2] Unexpected dimensions for " + texturePath);
                return;
            }
            m_MovementLabSpeedImages.Insert(speedImage);
        }
        m_MovementLabSpeedReady = m_MovementLabSpeedImages.Count() == 27;
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
        if (speedIcon < 0 || speedIcon > 26)
        {
            m_MovementLabSpeedRoot.Show(false);
            return;
        }
        HumanMovementState hudState = new HumanMovementState();
        speedPlayer.GetMovementState(hudState);
        if (speedMode == "AIM CROUCH" && hudState.m_iMovement == 0)
            speedIcon = 26;
        if (speedIcon != m_MovementLabLastIcon)
        {
            if (m_MovementLabLastIcon >= 0 && m_MovementLabLastIcon < m_MovementLabSpeedImages.Count())
                m_MovementLabSpeedImages[m_MovementLabLastIcon].Show(false);
            m_MovementLabSpeedImages[speedIcon].Show(true);
            m_MovementLabLastIcon = speedIcon;
        }
        // Anchor above the full native stamina strip, not its changing filled width.
        if (!m_Stamina)
            return;
        Widget speedAnchor = m_Stamina.GetParent();
        if (!speedAnchor)
            return;
        float speedX;
        float speedY;
        float speedW;
        float speedH;
        speedAnchor.GetScreenPos(speedX, speedY);
        speedAnchor.GetScreenSize(speedW, speedH);
        m_MovementLabSpeedRoot.SetScreenPos(speedX + speedW - 140, speedY - 76);
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
        }
        // Native DisplayStance can re-show these every frame; hide after super.Update.
        m_StanceStand.Show(false);
        m_StanceStandWalk.Show(false);
        m_StanceCrouch.Show(false);
        m_StanceProne.Show(false);
    }
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

}
