// Image-based stance/speed indicator. Reads selection; never controls movement.
modded class IngameHud
{
    protected bool m_MovementLabSpeedReady;
    protected ref MovementLabHeldItemCard m_MovementLabHeldCard;
    protected ImageWidget m_MovementLabStaminaBack;
    protected ImageWidget m_MovementLabStaminaFill;
    protected Widget m_MovementLabSpeedRoot;
    protected ref array<ImageWidget> m_MovementLabSpeedImages = new array<ImageWidget>();
    protected TextWidget m_MovementLabSpeedLabel;
    protected int m_MovementLabLastIcon = -1;

    override void Init(Widget hud_panel_widget)
    {
        super.Init(hud_panel_widget);
        m_MovementLabHeldCard = new MovementLabHeldItemCard(hud_panel_widget);
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
        MovementLabUpdateHeldHUD(speedPlayer, speedVisible);
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

    bool MovementLabHeldPanelReady()
    {
        return m_MovementLabHeldCard && m_MovementLabHeldCard.IsReady();
    }

    protected void MovementLabUpdateHeldHUD(PlayerBase player, bool visible)
    {
        if (!MovementLabHeldPanelReady())
            return;
        float screenW;
        float screenH;
        m_HudPanelWidget.GetScreenSize(screenW, screenH);
        float scale = screenH / 708;
        float cardWidth = 200 * scale;
        float cardHeight = 66 * scale;
        float cardX = 14 * scale;
        float cardY = screenH - cardHeight - 15 * scale;
        EntityAI heldItem;
        if (player)
            heldItem = player.GetEntityInHands();
        m_MovementLabHeldCard.Update(heldItem, visible, cardX, cardY, cardWidth, cardHeight);
        float indicatorW = 56 * scale;
        float indicatorH = 28 * scale;
        m_MovementLabSpeedRoot.SetScreenPos(cardX + cardWidth + 12 * scale, cardY + cardHeight - indicatorH);
        m_MovementLabSpeedRoot.SetSize(indicatorW, indicatorH);
        for (int indicatorIndex = 0; indicatorIndex < m_MovementLabSpeedImages.Count(); indicatorIndex++)
            m_MovementLabSpeedImages[indicatorIndex].SetSize(indicatorW, indicatorH);
        if (!m_MovementLabStaminaBack)
        {
            int staminaFlags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS | WidgetFlags.STRETCH | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND;
            m_MovementLabStaminaBack = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 4, 66, staminaFlags, 0x70383838, 20, m_HudPanelWidget));
            m_MovementLabStaminaFill = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 4, 66, staminaFlags, 0xFFFFFFFF, 21, m_HudPanelWidget));
            if (m_MovementLabStaminaBack && m_MovementLabStaminaFill)
            {
                m_MovementLabStaminaBack.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/solid.paa");
                m_MovementLabStaminaFill.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/solid.paa");
                m_MovementLabStaminaBack.SetImage(0);
                m_MovementLabStaminaFill.SetImage(0);
            }
        }
        if (m_MovementLabStaminaBack && m_MovementLabStaminaFill && m_Stamina)
        {
            m_MovementLabStaminaBack.Show(visible);
            m_MovementLabStaminaFill.Show(visible);
            float staminaFraction = 0;
            if (m_Stamina.GetMax() > 0)
                staminaFraction = Math.Clamp(m_Stamina.GetCurrent() / m_Stamina.GetMax(), 0, 1);
            m_MovementLabStaminaBack.SetScreenPos(cardX + cardWidth + 6 * scale, cardY);
            m_MovementLabStaminaBack.SetScreenSize(3 * scale, cardHeight);
            m_MovementLabStaminaFill.SetScreenPos(cardX + cardWidth + 6 * scale, cardY + cardHeight * (1 - staminaFraction));
            m_MovementLabStaminaFill.SetScreenSize(3 * scale, cardHeight * staminaFraction);
            m_Stamina.Show(false);
            if (m_StaminaBackground)
                m_StaminaBackground.Show(false);
        }
        if (m_Presence)
        {
            m_Presence.SetScreenPos(cardX + cardWidth + 70 * scale, cardY + cardHeight - 40);
            m_Presence.SetScreenSize(18, 40);
            MovementLabPositionNoiseBar(m_PresenceLevel0, 0, cardX + cardWidth + 70 * scale, cardY + cardHeight);
            MovementLabPositionNoiseBar(m_PresenceLevel1, 1, cardX + cardWidth + 70 * scale, cardY + cardHeight);
            MovementLabPositionNoiseBar(m_PresenceLevel2, 2, cardX + cardWidth + 70 * scale, cardY + cardHeight);
            MovementLabPositionNoiseBar(m_PresenceLevel3, 3, cardX + cardWidth + 70 * scale, cardY + cardHeight);
            MovementLabPositionNoiseBar(m_PresenceLevel4, 4, cardX + cardWidth + 70 * scale, cardY + cardHeight);
        }
    }

}
