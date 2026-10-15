// Static arms-only screen-space rendering proof. Not an animated viewmodel.
class MovementLabViewmodelUI
{
    protected static ref MovementLabViewmodelUI s_Instance;
    protected bool m_Enabled;
    protected int m_Frame;
    protected Widget m_Root;
    protected ItemPreviewWidget m_ArmsPreview;
    protected ItemPreviewWidget m_GunPreview;
    protected EntityAI m_ArmsItem;
    protected EntityAI m_CachedWeapon;
    protected PlayerBase m_HiddenPlayer;
    protected ref array<EntityAI> m_HiddenClothes = new array<EntityAI>();
    protected bool m_FaultLogged;
    protected bool m_WidgetAttempted;

    static MovementLabViewmodelUI GetInstance()
    {
        if (!s_Instance)
            s_Instance = new MovementLabViewmodelUI();
        return s_Instance;
    }
    static bool CanChange()
    {
        if (!GetGame() || GetGame().IsMultiplayer() || !GetGame().GetMission())
            return false;
        return GetGame().GetInput().HasGameFocus() && !GetGame().GetUIManager().GetMenu() && !GetGame().GetMission().IsPaused();
    }
    static void Toggle()
    {
        if (!CanChange())
            return;
        MovementLabViewmodelUI instance = GetInstance();
        instance.m_Enabled = !instance.m_Enabled;
        instance.m_WidgetAttempted = false;
        instance.m_FaultLogged = false;
        if (!instance.m_Enabled)
            instance.Stop();
        Print("[MovementLab Arms v2] Enabled=" + instance.m_Enabled);
    }
    static void CycleFrame()
    {
        if (!CanChange())
            return;
        MovementLabViewmodelUI instance = GetInstance();
        instance.m_Frame = (instance.m_Frame + 1) % 3;
        instance.ApplyFrame();
        Print("[MovementLab Arms v2] Framing=" + instance.m_Frame);
    }
    static void Tick()
    {
        if (s_Instance)
            s_Instance.Update();
    }
    static void Shutdown()
    {
        if (s_Instance)
            s_Instance.Stop();
        s_Instance = null;
    }
    void ~MovementLabViewmodelUI()
    {
        Stop();
        if (m_ArmsPreview)
            m_ArmsPreview.SetItem(null);
        if (m_GunPreview)
            m_GunPreview.SetItem(null);
        if (m_Root)
            m_Root.Unlink();
        // Only this local diagnostic item is owned; never delete the real gun.
        if (m_ArmsItem && GetGame())
            GetGame().ObjectDelete(m_ArmsItem);
    }
    protected bool EnsureWidget(PlayerBase player)
    {
        if (m_WidgetAttempted)
            return m_Root && m_ArmsPreview && m_GunPreview && m_ArmsItem;
        m_WidgetAttempted = true;
        if (!m_Root)
            m_Root = GetGame().GetWorkspace().CreateWidgets("MovementLabStartGate/GUI/MovementLabViewmodel.layout");
        if (!m_Root)
            return false;
        m_Root.SetFlags(WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS);
        m_Root.Show(false);
        m_ArmsPreview = ItemPreviewWidget.Cast(m_Root.FindAnyWidget("MovementLabArmsPreview"));
        m_GunPreview = ItemPreviewWidget.Cast(m_Root.FindAnyWidget("MovementLabGunPreview"));
        if (!m_ArmsPreview || !m_GunPreview)
            return false;
        m_ArmsPreview.SetFlags(WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND);
        m_GunPreview.SetFlags(WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND);
        if (!m_ArmsItem)
        {
            vector storagePosition = player.GetPosition();
            storagePosition[1] = storagePosition[1] - 1000;
            m_ArmsItem = EntityAI.Cast(GetGame().CreateObjectEx("MovementLabArmsPreviewItem", storagePosition, ECE_LOCAL | ECE_KEEPHEIGHT | ECE_NOLIFETIME | ECE_NOPERSISTENCY_WORLD));
        }
        if (!m_ArmsItem)
            return false;
        m_ArmsItem.DisableSimulation(true);
        m_ArmsPreview.SetItem(m_ArmsItem);
        m_ArmsPreview.SetView(0);
        ApplyFrame();
        return true;
    }
    protected void ApplyFrame()
    {
        if (!m_ArmsPreview || !m_GunPreview)
            return;
        // Fixed screen coordinates, independent of player/camera orientation.
        // These are native-test framing candidates, not calibrated grip transforms.
        m_ArmsPreview.SetPos(0.05, 0.32);
        m_ArmsPreview.SetSize(0.95, 0.75);
        m_ArmsPreview.SetModelOrientation("0 0 0");
        m_ArmsPreview.SetModelPosition("0 0 0");
        m_GunPreview.SetPos(0.28, 0.28);
        m_GunPreview.SetSize(0.64, 0.7);
        m_GunPreview.SetModelPosition("0 0 0");
        m_GunPreview.SetModelOrientation("0 0 0");
        if (m_Frame == 1)
            m_GunPreview.SetModelOrientation("0 90 0");
        if (m_Frame == 2)
        {
            m_ArmsPreview.SetPos(0.05, 0.2);
            m_ArmsPreview.SetSize(0.45, 0.65);
            m_GunPreview.SetPos(0.5, 0.2);
            m_GunPreview.SetSize(0.45, 0.65);
            m_GunPreview.SetModelOrientation("0 180 0");
        }
    }
    protected bool CanShow(PlayerBase player)
    {
        if (!m_Enabled || !MovementLabStartGate.Enabled || !CanChange() || !player)
            return false;
        if (!player.IsAlive() || player.IsUnconscious() || !player.IsRaised() || player.IsInThirdPerson())
            return false;
        if (player.IsInIronsights() || player.IsInOptics() || Camera.GetCurrentCamera())
            return false;
        if (!player.GetItemInHands() || !player.GetItemInHands().IsWeapon() || !player.GetInputController())
            return false;
        if (player.GetInputController().CameraIsFreeLook() || player.GetInputController().CameraIsTracking())
            return false;
        if (player.IsLiftWeapon() || player.IsWeaponObstructionBlockingADS() || !player.GetCommand_Move())
            return false;
        if (!player.GetWeaponManager() || player.GetWeaponManager().IsRunning())
            return false;
        // Native action playback is retained until separate action mirroring is tested.
        HumanCommandWeapons realWeapons = player.GetCommandModifier_Weapons();
        if (realWeapons && realWeapons.GetRunningAction() >= 0)
            return false;
        return true;
    }

    protected void LogFault(string message)
    {
        if (!m_FaultLogged)
        {
            Print("[MovementLab Arms v2] " + message);
            m_FaultLogged = true;
        }
    }

    protected void HideReal(PlayerBase player)
    {
        if (m_HiddenPlayer == player)
            return;
        m_HiddenPlayer = player;
        player.SetInvisible(true);
        if (player.GetItemAccessor())
            player.GetItemAccessor().HideItemInHands(true);
        for (int slot = 0; slot < 3; slot++)
        {
            string slotName = "Body";
            if (slot == 1)
                slotName = "Gloves";
            if (slot == 2)
                slotName = "Vest";
            EntityAI clothing = player.FindAttachmentBySlotName(slotName);
            if (clothing)
            {
                clothing.SetInvisible(true);
                m_HiddenClothes.Insert(clothing);
            }
        }
    }

    protected void Stop()
    {
        if (m_Root)
            m_Root.Show(false);
        if (m_HiddenPlayer && !m_HiddenPlayer.ToDelete())
        {
            m_HiddenPlayer.SetInvisible(false);
            if (m_HiddenPlayer.GetItemAccessor())
                m_HiddenPlayer.GetItemAccessor().HideItemInHands(false);
        }
        foreach (EntityAI clothing : m_HiddenClothes)
        {
            if (clothing && !clothing.ToDelete())
                clothing.SetInvisible(false);
        }
        m_HiddenClothes.Clear();
        m_HiddenPlayer = null;
        if (m_GunPreview)
            m_GunPreview.SetItem(null);
        m_CachedWeapon = null;
    }

    protected void Update()
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (!CanShow(player))
        {
            Stop();
            return;
        }
        if (!EnsureWidget(player))
        {
            Stop();
            LogFault("Arms model/widgets unavailable; native view retained.");
            return;
        }
        EntityAI held = player.GetItemInHands();
        if (held != m_CachedWeapon)
        {
            Stop();
            m_CachedWeapon = held;
            m_GunPreview.SetItem(held);
            m_GunPreview.SetView(held.GetViewIndex());
            ApplyFrame();
            Print("[MovementLab Arms v2] Fixed item preview=" + held.GetType());
        }
        if (m_GunPreview.GetItem() != held || m_ArmsPreview.GetItem() != m_ArmsItem)
        {
            Stop();
            LogFault("Preview item assignment failed; native view retained.");
            return;
        }
        HideReal(player);
        m_Root.Show(true);
    }
}

modded class IngameHud
{
    override void Update(float timeslice)
    {
        super.Update(timeslice);
        MovementLabViewmodelUI.Tick();
    }
}
