// Stance-only HUD; native item readout, stamina, sound and quickbar retained.
modded class IngameHud
{
    protected Widget m_MovementLabStanceRoot;
    protected ref array<ImageWidget> m_MovementLabStanceImages = new array<ImageWidget>();
    protected int m_MovementLabLastStanceIcon = -1;
    override void Init(Widget hud_panel_widget)
    {
        super.Init(hud_panel_widget);
        int flags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
        m_MovementLabStanceRoot = GetGame().GetWorkspace().CreateWidget(FrameWidgetTypeID, 0, 0, 120, 60, flags, 0xFFFFFFFF, 20, hud_panel_widget);
        if (!m_MovementLabStanceRoot)
            return;
        for (int i = 0; i < 6; i++)
        {
            ImageWidget icon = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 120, 60, flags | WidgetFlags.STRETCH | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND, 0xFFFFFFFF, 0, m_MovementLabStanceRoot));
            if (!icon)
                return;
            icon.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/stance_" + i + ".paa");
            icon.SetImage(0);
            icon.Show(false);
            m_MovementLabStanceImages.Insert(icon);
        }
        m_MovementLabStanceRoot.Show(false);
    }
    override void Update(float timeslice)
    {
        super.Update(timeslice);
        if (!m_MovementLabStanceRoot || !m_Stamina)
            return;
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        bool visible = MovementLabStartGate.Enabled && player && player.IsAlive() && !player.IsUnconscious() && m_MovementLabStanceImages.Count() == 6;
        if (!m_Presence || !m_Presence.IsVisibleHierarchy())
            visible = false;
        m_MovementLabStanceRoot.Show(visible);
        if (!visible)
            return;
        HumanMovementState state = new HumanMovementState();
        player.GetMovementState(state);
        int iconIndex = 0;
        if (state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_CROUCH || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDCROUCH)
            iconIndex = 2;
        else if (state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_PRONE || state.m_iStanceIdx == DayZPlayerConstants.STANCEIDX_RAISEDPRONE)
            iconIndex = 4;
        if (player.IsRaised())
            iconIndex = iconIndex + 1;
        if (m_MovementLabLastStanceIcon != iconIndex)
        {
            if (m_MovementLabLastStanceIcon >= 0)
                m_MovementLabStanceImages[m_MovementLabLastStanceIcon].Show(false);
            m_MovementLabStanceImages[iconIndex].Show(true);
            m_MovementLabLastStanceIcon = iconIndex;
        }
        float x;
        float y;
        float w;
        float h;
        m_Stamina.GetScreenPos(x, y);
        m_Stamina.GetScreenSize(w, h);
        float screenW;
        float screenH;
        m_HudPanelWidget.GetScreenSize(screenW, screenH);
        float scale = screenH / 1080;
        float iconWidth = 120 * scale;
        float iconHeight = 60 * scale;
        m_MovementLabStanceRoot.SetScreenPos(x + w - iconWidth, y - iconHeight - 4 * scale);
        m_MovementLabStanceRoot.SetSize(iconWidth, iconHeight);
        foreach (ImageWidget stanceImage: m_MovementLabStanceImages)
            stanceImage.SetSize(iconWidth, iconHeight);
        m_StanceStand.Show(false);
        m_StanceStandWalk.Show(false);
        m_StanceCrouch.Show(false);
        m_StanceProne.Show(false);
    }
}
