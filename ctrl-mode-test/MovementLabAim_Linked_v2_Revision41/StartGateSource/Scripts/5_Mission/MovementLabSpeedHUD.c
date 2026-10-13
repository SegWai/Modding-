modded class IngameHud
{
    protected bool m_MovementLabSpeedReady;
    protected Widget m_MovementLabSpeedRoot;
    protected TextWidget m_MovementLabSpeedLabel;
    protected ref array<TextWidget> m_MovementLabSpeedCells = new array<TextWidget>();

    override void Init(Widget hud_panel_widget)
    {
        super.Init(hud_panel_widget);
        m_MovementLabSpeedReady = false;
        m_MovementLabSpeedCells.Clear();
        m_MovementLabSpeedRoot = hud_panel_widget.FindAnyWidget("MovementLabSpeedIndicator");
        WidgetFlags speedFlags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS;
        speedFlags = speedFlags | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE;
        speedFlags = speedFlags | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
        if (!m_MovementLabSpeedRoot)
        {
            m_MovementLabSpeedRoot = GetGame().GetWorkspace().CreateWidget(FrameWidgetTypeID, 0, 0, 150, 44, speedFlags, 0xFFFFFFFF, 20, hud_panel_widget);
            if (!m_MovementLabSpeedRoot)
            {
                Print("[MovementLab HUD] Could not create speed indicator.");
                return;
            }
            m_MovementLabSpeedRoot.SetName("MovementLabSpeedIndicator");
        }
        m_MovementLabSpeedRoot.Show(false);
        m_MovementLabSpeedLabel = TextWidget.Cast(m_MovementLabSpeedRoot.FindAnyWidget("MovementLabSpeedLabel"));
        if (!m_MovementLabSpeedLabel)
        {
            m_MovementLabSpeedLabel = TextWidget.Cast(GetGame().GetWorkspace().CreateWidget(TextWidgetTypeID, 0, 28, 150, 16, speedFlags, 0xFFFFFFFF, 0, m_MovementLabSpeedRoot));
            if (m_MovementLabSpeedLabel)
            {
                m_MovementLabSpeedLabel.SetName("MovementLabSpeedLabel");
                m_MovementLabSpeedLabel.SetTextExactSize(12);
                m_MovementLabSpeedLabel.SetOutline(1);
            }
        }
        for (int speedCellIndex = 0; speedCellIndex < 5; speedCellIndex++)
        {
            string speedCellName = "MovementLabSpeedCell" + speedCellIndex;
            TextWidget speedCell = TextWidget.Cast(m_MovementLabSpeedRoot.FindAnyWidget(speedCellName));
            if (!speedCell)
            {
                speedCell = TextWidget.Cast(GetGame().GetWorkspace().CreateWidget(TextWidgetTypeID, speedCellIndex * 12, 0, 12, 28, speedFlags, 0xFFFFFFFF, 0, m_MovementLabSpeedRoot));
                if (speedCell)
                {
                    speedCell.SetName(speedCellName);
                    speedCell.SetText("|");
                    speedCell.SetTextExactSize(26);
                    speedCell.SetBold(true);
                    speedCell.SetOutline(1);
                }
            }
            m_MovementLabSpeedCells.Insert(speedCell);
        }
        if (!m_MovementLabSpeedLabel || m_MovementLabSpeedCells.Count() != 5)
            return;
        foreach (TextWidget readyCell: m_MovementLabSpeedCells)
        {
            if (!readyCell)
                return;
        }
        m_MovementLabSpeedReady = true;
        Print("[MovementLab HUD] Five-step speed indicator initialized.");
        m_MovementLabSpeedRoot.Show(false);
    }

    override void Update(float timeslice)
    {
        super.Update(timeslice);
        if (!m_MovementLabSpeedRoot)
            return;
        PlayerBase speedPlayer = PlayerBase.Cast(GetGame().GetPlayer());
        bool speedVisible = m_MovementLabSpeedReady && MovementLabStartGate.Enabled && speedPlayer && speedPlayer.IsAlive() && !speedPlayer.IsUnconscious();
        if (!m_Presence || !m_Presence.IsVisibleHierarchy() || !m_MovementLabSpeedLabel)
            speedVisible = false;
        m_MovementLabSpeedRoot.Show(speedVisible);
        if (!speedVisible)
            return;
        int speedLevel;
        string speedMode;
        bool speedAuto;
        speedPlayer.MovementLabGetHUDSpeed(speedLevel, speedMode, speedAuto);
        speedLevel = Math.Clamp(speedLevel, 1, 5);
        for (int speedBarIndex = 0; speedBarIndex < m_MovementLabSpeedCells.Count(); speedBarIndex++)
        {
            TextWidget speedBar = m_MovementLabSpeedCells[speedBarIndex];
            if (!speedBar)
                continue;
            int speedBarColor = ARGB(70, 255, 255, 255);
            if (speedBarIndex < speedLevel)
            {
                speedBarColor = ARGB(255, 255, 255, 255);
                if (speedAuto)
                    speedBarColor = ARGB(255, 235, 193, 100);
            }
            speedBar.SetColor(speedBarColor);
        }
        string speedLabel = speedMode + " " + speedLevel;
        if (speedAuto)
            speedLabel = speedLabel + " AUTO";
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
        float maxSpeedX = Math.Max(0, viewW - 150);
        float maxSpeedY = Math.Max(0, viewH - 44);
        float panelSpeedX = Math.Clamp(speedRight + 12, 0, maxSpeedX);
        float panelSpeedY = Math.Clamp(speedY, 0, maxSpeedY);
        m_MovementLabSpeedRoot.SetScreenPos(panelSpeedX, panelSpeedY);
    }
}
