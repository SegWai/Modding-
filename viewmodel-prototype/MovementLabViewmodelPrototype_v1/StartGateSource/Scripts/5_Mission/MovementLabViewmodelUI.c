// Experimental separate screen-space avatar renderer. Never changes camera
// transforms or copies mouse/world orientation into the dummy pose.
class MovementLabViewmodelUI
{
    protected static ref MovementLabViewmodelUI s_Instance;
    protected bool m_Enabled;
    protected int m_Frame;
    protected Widget m_Root;
    protected PlayerPreviewWidget m_Preview;
    protected PlayerBase m_CachedPlayer;
    protected EntityAI m_CachedWeapon;
    protected DayZPlayer m_Dummy;
    protected int m_PoseVar = -1;
    protected int m_AimXVar = -1;
    protected int m_AimYVar = -1;
    protected int m_AimIKVar = -1;
    protected int m_RaisedVar = -1;
    protected PlayerBase m_HiddenPlayer;
    protected ref array<EntityAI> m_HiddenClothes = new array<EntityAI>();
    protected bool m_FaultLogged;
    protected bool m_WidgetAttempted;
    protected int m_BindTime = -1000;

    static MovementLabViewmodelUI GetInstance()
    {
        if (!s_Instance)
            s_Instance = new MovementLabViewmodelUI();
        return s_Instance;
    }

    static bool CanChange()
    {
        if (!GetGame() || GetGame().IsMultiplayer())
            return false;
        return GetGame().GetInput().HasGameFocus() && !GetGame().GetUIManager().GetMenu() && !GetGame().GetMission().IsPaused();
    }

    static void Toggle()
    {
        if (!CanChange())
            return;
        MovementLabViewmodelUI instance = GetInstance();
        instance.m_Enabled = !instance.m_Enabled;
        if (instance.m_Enabled)
        {
            instance.m_WidgetAttempted = false;
            instance.m_FaultLogged = false;
        }
        if (!instance.m_Enabled)
            instance.Stop();
        Print("[MovementLab Viewmodel v1] Enabled=" + instance.m_Enabled);
    }

    static void CycleFrame()
    {
        if (!CanChange())
            return;
        MovementLabViewmodelUI instance = GetInstance();
        instance.m_Frame = (instance.m_Frame + 1) % 3;
        instance.ApplyFrame();
        Print("[MovementLab Viewmodel v1] Framing preset=" + instance.m_Frame);
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
        if (m_Root)
            m_Root.Unlink();
    }

    protected bool EnsureWidget()
    {
        if (!m_Root && m_WidgetAttempted)
            return false;
        if (!m_Root)
        {
            m_WidgetAttempted = true;
            m_Root = GetGame().GetWorkspace().CreateWidgets("MovementLabStartGate/GUI/MovementLabViewmodel.layout");
            if (m_Root)
            {
                m_Root.SetFlags(WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS);
                m_Root.Show(false);
                m_Preview = PlayerPreviewWidget.Cast(m_Root.FindAnyWidget("MovementLabViewmodelPreview"));
                if (m_Preview)
                {
                    m_Preview.SetFlags(WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS);
                    m_Preview.SetFlags(WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND);
                    ApplyFrame();
                }
            }
        }
        return m_Root && m_Preview;
    }

    protected void ApplyFrame()
    {
        if (!m_Preview)
            return;
        // Inventory-preview orientation uses its second component for yaw.
        m_Preview.SetModelOrientation("0 180 0");
        m_Preview.SetPos(0.18, 0.1);
        m_Preview.SetSize(0.82, 0.9);
        m_Preview.SetModelPosition("0 -0.65 0.18");
        if (m_Frame == 1)
            m_Preview.SetModelPosition("0 -0.8 0.05");
        if (m_Frame == 2)
        {
            // Wide framing verifies that the separate avatar actually renders.
            m_Preview.SetPos(0.45, 0.15);
            m_Preview.SetSize(0.55, 0.85);
            m_Preview.SetModelPosition("0 0 0.605");
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
            Print("[MovementLab Viewmodel v1] " + message);
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
        if (m_Dummy && m_Dummy != m_CachedPlayer && m_PoseVar >= 0 && !m_Dummy.ToDelete())
            m_Dummy.AnimSetFloat(m_PoseVar, 0);
    }

    protected void Update()
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (!CanShow(player))
        {
            Stop();
            return;
        }
        if (!EnsureWidget())
        {
            Stop();
            LogFault("Preview widget unavailable; native view retained.");
            return;
        }
        EntityAI held = player.GetItemInHands();
        if (player != m_CachedPlayer || held != m_CachedWeapon)
        {
            Stop();
            m_CachedPlayer = player;
            m_CachedWeapon = held;
            m_Dummy = null;
            m_PoseVar = -1;
            m_Preview.SetPlayer(player);
            m_FaultLogged = false;
            Print("[MovementLab Viewmodel v1] Bound separate preview to " + held.GetType());
        }
        m_Preview.UpdateItemInHands(held);
        DayZPlayer previewDummy = m_Preview.GetDummyPlayer();
        if (!previewDummy || previewDummy == player || !previewDummy.GetAnimInterface())
        {
            Stop();
            LogFault("Independent animated preview dummy not ready; native view retained.");
            return;
        }
        if (previewDummy != m_Dummy || m_PoseVar < 0)
        {
            int previewBindNow = GetGame().GetTime();
            if (previewDummy == m_Dummy && previewBindNow - m_BindTime < 500)
            {
                Stop();
                return;
            }
            m_BindTime = previewBindNow;
            m_Dummy = previewDummy;
            HumanAnimInterface previewAnim = m_Dummy.GetAnimInterface();
            m_PoseVar = previewAnim.BindVariableFloat("MovementLabViewmodelPreview");
            m_AimXVar = previewAnim.BindVariableFloat("AimX");
            m_AimYVar = previewAnim.BindVariableFloat("AimY");
            m_AimIKVar = previewAnim.BindVariableFloat("AimIKX");
            m_RaisedVar = previewAnim.BindVariableBool("Raised");
            Print("[MovementLab Viewmodel v1] Dummy pose binding=" + m_PoseVar);
        }
        if (m_PoseVar < 0)
        {
            Stop();
            LogFault("Dummy does not expose patched pose variable; native view retained.");
            return;
        }
        m_Dummy.AnimSetFloat(m_PoseVar, 1);
        if (m_AimXVar >= 0)
            m_Dummy.AnimSetFloat(m_AimXVar, 0);
        if (m_AimYVar >= 0)
            m_Dummy.AnimSetFloat(m_AimYVar, 0);
        if (m_AimIKVar >= 0)
            m_Dummy.AnimSetFloat(m_AimIKVar, 0);
        if (m_RaisedVar >= 0)
            m_Dummy.AnimSetBool(m_RaisedVar, true);
        m_Dummy.SetInvisible(false);
        if (m_Dummy.GetItemAccessor())
            m_Dummy.GetItemAccessor().HideItemInHands(false);
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
