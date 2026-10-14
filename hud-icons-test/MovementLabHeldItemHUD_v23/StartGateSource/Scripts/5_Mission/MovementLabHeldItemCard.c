// One current-item panel, independent of numbered quickslots.
class MovementLabHeldItemCard
{
    protected Widget m_Root;
    protected string m_ArialTitleText;
    protected string m_ArialCalibreText;
    protected string m_ArialModeText;
    protected string m_ArialRoundsText;
    protected ref MovementLabArialLine m_ArialTitle = new MovementLabArialLine();
    protected ref MovementLabArialLine m_ArialCalibre = new MovementLabArialLine();
    protected ref MovementLabArialLine m_ArialMode = new MovementLabArialLine();
    protected ref MovementLabArialLine m_ArialRounds = new MovementLabArialLine();
    protected ItemPreviewWidget m_Preview;
    protected EntityAI m_StaticWeaponPreview;
    protected EntityAI m_StaticWeaponSource;
    protected string m_StaticAttachmentSignature;
    protected int m_StaticNextAttachmentCheck;

    void MovementLabHeldItemCard(Widget parent)
    {
        m_Root = GetGame().GetWorkspace().CreateWidgets("MovementLabStartGate/GUI/MovementLabHeldItem.layout", parent);
        if (m_Root)
        {
            m_Preview = ItemPreviewWidget.Cast(m_Root.FindAnyWidget("MovementLabHeldRender"));
            if (m_Preview)
                m_Preview.SetSort(1);

        }
    }

    bool IsReady()
    {
        return m_Root && m_Preview;
    }

    void Update(EntityAI item, bool visible, float x, float y, float width, float height)
    {
        if (!IsReady())
            return;
        m_Root.Show(visible && item != null);
        if (!visible || !item)
        {
            m_Preview.SetItem(null);
            if (!item)
                MovementLabClearStaticWeapon();
            return;
        }
        m_Root.SetScreenPos(x, y);
        m_Root.SetScreenSize(width, height);
        MovementLabUpdateCard(m_Root, m_Root, item);
        // 2.5pt at Photoshop300dpi reference; screen scaling follows card height.
        float fontPixels = 8.8 * height / 66;
        m_ArialTitle.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardName")), m_ArialTitleText, true, fontPixels);
        m_ArialCalibre.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardCalibre")), m_ArialCalibreText, Weapon.Cast(item) != null, fontPixels);
        m_ArialMode.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardMode")), m_ArialModeText, Weapon.Cast(item) != null, fontPixels);
        m_ArialRounds.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardRounds")), m_ArialRoundsText, Weapon.Cast(item) != null, fontPixels);
        float fraction = 0.86;
        if (!item.IsWeapon())
            fraction = 0.60;
        else if (GetGame().IsKindOf(item.GetType(), "Pistol_Base"))
            fraction = 0.70;
        float inset = (1 - fraction) * 0.5;
        m_Preview.SetPos(inset, inset);
        m_Preview.SetSize(fraction, fraction);
        EntityAI displayItem = item;
        if (item.IsWeapon())
        {
            displayItem = MovementLabStaticWeapon(item);
            if (!displayItem)
            {
                m_Preview.SetItem(null);
                return;
            }
        }
        else
            MovementLabClearStaticWeapon();
        if (m_Preview.GetItem() != displayItem)
        {
            m_Preview.SetItem(displayItem);
            m_Preview.SetModelPosition("0 0 0");
            m_Preview.SetModelOrientation("0 0 0");
            m_Preview.SetView(item.GetViewIndex());
        }
    }
    protected Widget MovementLabCardWidget(Widget parent, string name, WidgetType kind, float x, float y, float w, float h, int color)
    {
        Widget result = parent.FindAnyWidget(name);
        int flags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
        if (!result)
        {
            result = GetGame().GetWorkspace().CreateWidget(kind, x, y, w, h, flags, color, -1, parent);
            if (!result)
                return null;
            result.SetName(name);
            ImageWidget image = ImageWidget.Cast(result);
            if (image)
            {
                image.SetFlags(WidgetFlags.STRETCH | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND);
                string imageTexture = "MovementLabStartGate/GUI/Textures/solid.paa";
                if (name == "MLCardBackground")
                    imageTexture = "MovementLabStartGate/GUI/Textures/held-background.paa";
                image.LoadImageFile(0, imageTexture);
                image.SetImage(0);
            }
            TextWidget text = TextWidget.Cast(result);
            if (text)
            {
                result.SetSort(2);
                text.SetBold(true);
                text.SetTextExactSize(9);
                text.SetOutline(1, 0xCC000000);
                text.SetShadow(3, 0xFF000000, 0.8, 1, 1);
            }
        }
        result.SetPos(x, y);
        result.SetSize(w, h);
        result.SetColor(color);
        return result;
    }

    protected string MovementLabCalibre(EntityAI item)
    {
        TStringArray ammunition = new TStringArray();
        GetGame().ConfigGetTextArray("CfgWeapons " + item.GetType() + " chamberableFrom", ammunition);
        if (ammunition.Count() == 0)
            return "";
        string ammo = ammunition[0];
        switch (ammo)
        {
            case "Ammo_762x39": return "7.62x39";
            case "Ammo_762x54": return "7.62x54R";
            case "Ammo_762x51": return "7.62x51";
            case "Ammo_556x45": return "5.56x45";
            case "Ammo_545x39": return "5.45x39";
            case "Ammo_9x19": return "9x19";
            case "Ammo_380": return ".380";
            case "Ammo_45ACP": return ".45 ACP";
            case "Ammo_357": return ".357";
            case "Ammo_22": return ".22 LR";
            case "Ammo_12gaPellets": return "12 GA";
        }
        string ammoLabel;
        GetGame().ConfigGetText("CfgMagazines " + ammo + " displayName", ammoLabel);
        return Widget.TranslateString(ammoLabel);
    }

    protected void MovementLabUpdateCard(Widget slot, Widget root, EntityAI item)
    {
        m_ArialTitleText = "";
        m_ArialCalibreText = "";
        m_ArialModeText = "";
        m_ArialRoundsText = "";
        float width;
        float height;
        slot.GetScreenSize(width, height);
        slot.ClearFlags(WidgetFlags.CLIPCHILDREN);
        root.ClearFlags(WidgetFlags.CLIPCHILDREN);
        MovementLabCardWidget(root, "MLCardBackground", ImageWidgetTypeID, 0, 0, width, height, 0xFFFFFFFF);
        MovementLabCardWidget(root, "MLCardTop", ImageWidgetTypeID, 0, 0, width, 1, 0xFF101010);
        MovementLabCardWidget(root, "MLCardBottom", ImageWidgetTypeID, 0, height - 1, width, 1, 0xFF101010);
        MovementLabCardWidget(root, "MLCardLeft", ImageWidgetTypeID, 0, 0, 1, height, 0xFF101010);
        MovementLabCardWidget(root, "MLCardRight", ImageWidgetTypeID, width - 1, 0, 1, height, 0xFF101010);
        TextWidget name = TextWidget.Cast(MovementLabCardWidget(root, "MLCardName", TextWidgetTypeID, 3, -16, width * 0.68, 14, 0xFFFFFFFF));
        TextWidget calibre = TextWidget.Cast(MovementLabCardWidget(root, "MLCardCalibre", TextWidgetTypeID, width * 0.68, -16, width * 0.30, 14, 0xFFFFFFFF));
        TextWidget fireMode = TextWidget.Cast(MovementLabCardWidget(root, "MLCardMode", TextWidgetTypeID, 3, height - 14, width * 0.48, 13, 0xFFFFFFFF));
        TextWidget rounds = TextWidget.Cast(MovementLabCardWidget(root, "MLCardRounds", TextWidgetTypeID, width * 0.68, height - 14, width * 0.3, 13, 0xFFFFFFFF));
        Widget health = MovementLabCardWidget(root, "MLCardHealth", ImageWidgetTypeID, width - 4, 0, 3, height, 0xFF40FF00);
        Weapon firearm = Weapon.Cast(item);
        if (name)
        {
            string title = "";
            if (item)
                title = item.GetDisplayName();
            title.ToUpper();
            int limit = Math.Max(6, Math.Floor(width * 0.68 / 5));
            if (title.Length() > limit)
                title = title.Substring(0, limit - 1) + ".";
            m_ArialTitleText = title;
            name.SetText(title);
        }
        if (calibre)
        {
            calibre.Show(firearm != null);
            if (firearm)
            {
                m_ArialCalibreText = MovementLabCalibre(item);
                calibre.SetText(m_ArialCalibreText);
            }
        }
        if (health)
        {
            health.Show(firearm != null);
            if (firearm)
            {
                float condition = Math.Clamp(item.GetHealth01("", "Health"), 0, 1);
                health.SetPos(width - 4, height * (1 - condition));
                health.SetSize(3, height * condition);
                health.SetColor(0xFF000000 | ItemManager.GetItemHealthColor(item));
            }
        }
        if (fireMode)
            fireMode.Show(firearm != null);
        if (rounds)
            rounds.Show(firearm != null);
        if (firearm)
        {
            int muzzle = firearm.GetCurrentMuzzle();
            string mode = "I";
            if (firearm.GetCurrentModeAutoFire(muzzle))
                mode = "IIIII";
            else if (firearm.GetCurrentModeBurstSize(muzzle) > 1)
                mode = "III";
            m_ArialModeText = mode;
            if (fireMode)
                fireMode.SetText(mode);
            int count = 0;
            Magazine magazine = firearm.GetMagazine(muzzle);
            if (magazine)
                count = magazine.GetAmmoCount();
            if (!firearm.IsChamberEmpty(muzzle) && !firearm.IsChamberFiredOut(muzzle))
                count = count + 1;
            if (rounds)
                {
                    int capacity = 1;
                    if (magazine)
                        capacity = magazine.GetAmmoMax();
                    m_ArialRoundsText = count.ToString() + "/" + capacity.ToString();
                    rounds.SetText(m_ArialRoundsText);
                }
        }
    }

    void ~MovementLabHeldItemCard()
    {
        MovementLabClearStaticWeapon();
    }

    protected void MovementLabClearStaticWeapon()
    {
        if (m_StaticWeaponPreview)
        {
            if (m_Preview)
                m_Preview.SetItem(null);
            GetGame().ObjectDelete(m_StaticWeaponPreview);
        }
        m_StaticWeaponPreview = null;
        m_StaticWeaponSource = null;
        m_StaticAttachmentSignature = "";
    }

    protected string MovementLabAttachmentSignature(EntityAI source, int depth)
    {
        string signature = source.GetType();
        if (depth >= 3)
            return signature;
        for (int attachmentIndex = 0; attachmentIndex < source.GetInventory().AttachmentCount(); attachmentIndex++)
        {
            EntityAI attachment = source.GetInventory().GetAttachmentFromIndex(attachmentIndex);
            if (attachment)
                signature = signature + "|" + MovementLabAttachmentSignature(attachment, depth + 1);
        }
        return signature;
    }

    protected void MovementLabCopyPreviewAttachments(EntityAI source, EntityAI target, int depth)
    {
        if (depth >= 3)
            return;
        for (int copyIndex = 0; copyIndex < source.GetInventory().AttachmentCount(); copyIndex++)
        {
            EntityAI sourceAttachment = source.GetInventory().GetAttachmentFromIndex(copyIndex);
            if (!sourceAttachment)
                continue;
            EntityAI copyAttachment = target.GetInventory().CreateAttachment(sourceAttachment.GetType());
            if (!copyAttachment)
                continue;
            copyAttachment.SetAllowDamage(false);
            copyAttachment.DisableSimulation(true);
            MovementLabCopyPreviewAttachments(sourceAttachment, copyAttachment, depth + 1);
        }
    }

    protected EntityAI MovementLabStaticWeapon(EntityAI source)
    {
        int now = GetGame().GetTime();
        bool changed = source != m_StaticWeaponSource || !m_StaticWeaponPreview;
        if (!changed && now < m_StaticNextAttachmentCheck)
            return m_StaticWeaponPreview;
        m_StaticNextAttachmentCheck = now + 500;
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        // Keep the thumbnail snapshot stable while reload temporarily removes magazines.
        if (!changed && player && player.GetWeaponManager() && player.GetWeaponManager().IsRunning())
            return m_StaticWeaponPreview;
        string signature = MovementLabAttachmentSignature(source, 0);
        if (!changed && signature == m_StaticAttachmentSignature)
            return m_StaticWeaponPreview;
        MovementLabClearStaticWeapon();
        vector storagePosition = "0 -1000 0";
        if (player)
        {
            storagePosition = player.GetPosition();
            storagePosition[1] = storagePosition[1] - 1000;
        }
        m_StaticWeaponPreview = EntityAI.Cast(GetGame().CreateObjectEx(source.GetType(), storagePosition, ECE_LOCAL | ECE_KEEPHEIGHT | ECE_NOLIFETIME | ECE_NOPERSISTENCY_WORLD));
        if (!m_StaticWeaponPreview)
            return null;
        MovementLabCopyPreviewAttachments(source, m_StaticWeaponPreview, 0);
        m_StaticWeaponPreview.SetAllowDamage(false);
        m_StaticWeaponPreview.DisableSimulation(true);
        m_StaticWeaponSource = source;
        m_StaticAttachmentSignature = signature;
        return m_StaticWeaponPreview;
    }

}
