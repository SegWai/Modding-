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
    protected RTTextureWidget m_SupersampleTexture;
    protected ItemPreviewWidget m_SupersampleItem;
    protected ImageWidget m_SupersampleOutput;
    protected float m_SupersampleLastWidth;
    protected float m_SupersampleLastHeight;
    protected bool m_SupersampleReported;
    protected bool m_FireModeIconsReady;
    protected ref array<ImageWidget> m_FireModeImages = new array<ImageWidget>();
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
            MovementLabHideSupersample();
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
        m_ArialCalibre.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardCalibre")), m_ArialCalibreText, Weapon.Cast(item) != null, fontPixels, true);
        m_ArialMode.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardMode")), m_ArialModeText, false, fontPixels);
        m_ArialRounds.Update(TextWidget.Cast(m_Root.FindAnyWidget("MLCardRounds")), m_ArialRoundsText, Weapon.Cast(item) != null, fontPixels, true);
        MovementLabUpdateFireModeIcons(item, width, height, fontPixels);
        float fraction = 0.86;
        if (!item.IsWeapon())
            fraction = 0.60;
        else if (GetGame().IsKindOf(item.GetType(), "Pistol_Base"))
            fraction = 0.70;
        float inset = (1 - fraction) * 0.5;
        float previewY = inset;
        if (item.IsWeapon())
            previewY = Math.Max(0, inset - 0.03);
        m_Preview.SetPos(inset, previewY);
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
        MovementLabUpdateSupersample(displayItem, item.GetViewIndex(), width, height, fraction, inset, previewY);
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
                    imageTexture = "MovementLabStartGate/GUI/Textures/held-background-original.paa";
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
        // Keep uploaded alpha fade; multiply RGB by black without reducing alpha.
        MovementLabCardWidget(root, "MLCardBackground", ImageWidgetTypeID, 0, 0, width, height, 0xFF000000);
        TextWidget name = TextWidget.Cast(MovementLabCardWidget(root, "MLCardName", TextWidgetTypeID, 3, -16, width * 0.68, 14, 0xFFFFFFFF));
        TextWidget calibre = TextWidget.Cast(MovementLabCardWidget(root, "MLCardCalibre", TextWidgetTypeID, width * 0.68, -16, width * 0.30, 14, 0xFFFFFFFF));
        TextWidget fireMode = TextWidget.Cast(MovementLabCardWidget(root, "MLCardMode", TextWidgetTypeID, 3, height - 14, width * 0.48, 13, 0xFFFFFFFF));
        TextWidget rounds = TextWidget.Cast(MovementLabCardWidget(root, "MLCardRounds", TextWidgetTypeID, width * 0.38, height - 14, width * 0.46, 13, 0xFFFFFFFF));
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
            int capacity = 0;
            Magazine magazine = firearm.GetMagazine(muzzle);
            if (magazine)
            {
                count = magazine.GetAmmoCount();
                capacity = magazine.GetAmmoMax();
            }
            else if (firearm.HasInternalMagazine(muzzle))
            {
                count = firearm.GetInternalMagazineCartridgeCount(muzzle);
                capacity = firearm.GetInternalMagazineMaxCartridgeCount(muzzle);
            }
            // Magazine count stays separate; show only a live cartridge in the active chamber.
            m_ArialRoundsText = count.ToString() + "/" + capacity.ToString();
            if (!firearm.IsChamberEmpty(muzzle) && !firearm.IsChamberFiredOut(muzzle))
                m_ArialRoundsText = "(1) " + m_ArialRoundsText;
            if (rounds)
                rounds.SetText(m_ArialRoundsText);

        }
    }

    void ~MovementLabHeldItemCard()
    {
        MovementLabHideSupersample();
        if (m_SupersampleTexture)
            m_SupersampleTexture.Unlink();
        MovementLabClearStaticWeapon();
    }

    protected void MovementLabClearStaticWeapon()
    {
        if (m_StaticWeaponPreview)
        {
            if (m_SupersampleItem)
                m_SupersampleItem.SetItem(null);
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
            {
                InventoryLocation attachmentLocation = new InventoryLocation();
                attachment.GetInventory().GetCurrentInventoryLocation(attachmentLocation);
                signature = signature + "|" + attachmentLocation.GetSlot();
                signature = signature + ":" + MovementLabAttachmentSignature(attachment, depth + 1);
            }
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
            InventoryLocation sourceLocation = new InventoryLocation();
            sourceAttachment.GetInventory().GetCurrentInventoryLocation(sourceLocation);
            EntityAI copyAttachment = target.GetInventory().CreateAttachmentEx(sourceAttachment.GetType(), sourceLocation.GetSlot());
            if (!copyAttachment)
                copyAttachment = target.GetInventory().CreateAttachment(sourceAttachment.GetType());
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
        m_StaticNextAttachmentCheck = now + 150;
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        string signature = MovementLabAttachmentSignature(source, 0);
        Weapon sourceWeapon = Weapon.Cast(source);
        if (sourceWeapon)
        {
            for (int muzzleIndex = 0; muzzleIndex < sourceWeapon.GetMuzzleCount(); muzzleIndex++)
            {
                Magazine sourceMagazine = sourceWeapon.GetMagazine(muzzleIndex);
                signature = signature + "|MAG" + muzzleIndex;
                if (sourceMagazine)
                    signature = signature + ":" + sourceMagazine.GetType();
                else
                    signature = signature + ":NONE";
            }
        }
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
        // Freeze the independent model before attachment events can advance its pose.
        m_StaticWeaponPreview.SetAllowDamage(false);
        m_StaticWeaponPreview.DisableSimulation(true);
        MovementLabCopyPreviewAttachments(source, m_StaticWeaponPreview, 0);
        Weapon_Base previewWeapon = Weapon_Base.Cast(m_StaticWeaponPreview);
        if (sourceWeapon && previewWeapon)
        {
            bool hasMagazine = false;
            for (int magazineMuzzle = 0; magazineMuzzle < sourceWeapon.GetMuzzleCount(); magazineMuzzle++)
            {
                Magazine realMagazine = sourceWeapon.GetMagazine(magazineMuzzle);
                if (!realMagazine)
                    continue;
                hasMagazine = true;
                Magazine copiedMagazine = previewWeapon.GetMagazine(magazineMuzzle);
                if (!copiedMagazine)
                {
                    EntityAI magazineCopy = previewWeapon.GetInventory().CreateAttachmentEx(realMagazine.GetType(), previewWeapon.GetSlotFromMuzzleIndex(magazineMuzzle));
                    if (!magazineCopy)
                        magazineCopy = previewWeapon.GetInventory().CreateAttachment(realMagazine.GetType());
                    if (magazineCopy)
                    {
                        magazineCopy.SetAllowDamage(false);
                        magazineCopy.DisableSimulation(true);
                    }
                }
            }
            // Direct static visual state: do not post reload/weapon-animation events.
            previewWeapon.SyncSelectionState(false, hasMagazine);
            if (hasMagazine)
                previewWeapon.ShowMagazine();
            else
                previewWeapon.HideMagazine();
            Print("[MovementLab preview v25] " + source.GetType() + " source magazine visible=" + hasMagazine);
        }
        m_StaticWeaponSource = source;
        m_StaticAttachmentSignature = signature;
        return m_StaticWeaponPreview;
    }

    protected void MovementLabUpdateFireModeIcons(EntityAI item, float width, float height, float fontPixels)
    {
        float iconSize = fontPixels * 1.10;
        if (!m_FireModeIconsReady)
        {
            m_FireModeImages.Clear();
            for (int modeIndex = 0; modeIndex < 3; modeIndex++)
            {
                string imageName = "MLFireModeIcon" + modeIndex;
                ImageWidget modeImage = ImageWidget.Cast(MovementLabCardWidget(m_Root, imageName, ImageWidgetTypeID, width * 0.87, height - 14, iconSize, iconSize, 0xFFFFFFFF));
                if (!modeImage)
                    return;
                modeImage.SetSort(3);
                if (!modeImage.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/fire_mode_" + modeIndex + ".paa"))
                    return;
                modeImage.SetImage(0);
                modeImage.Show(false);
                m_FireModeImages.Insert(modeImage);
            }
            m_FireModeIconsReady = m_FireModeImages.Count() == 3;
        }
        Weapon firearm = Weapon.Cast(item);
        int picked = 0;
        if (firearm)
        {
            int currentMuzzle = firearm.GetCurrentMuzzle();
            if (firearm.GetCurrentModeAutoFire(currentMuzzle))
                picked = 2;
            else if (firearm.GetCurrentModeBurstSize(currentMuzzle) > 1)
                picked = 1;
        }
        for (int iconIndex = 0; iconIndex < m_FireModeImages.Count(); iconIndex++)
        {
            m_FireModeImages[iconIndex].SetPos(width * 0.87, height - 14);
            m_FireModeImages[iconIndex].SetSize(iconSize, iconSize);
            m_FireModeImages[iconIndex].Show(firearm != null && iconIndex == picked);
        }
    }

    protected void MovementLabHideSupersample()
    {
        if (m_SupersampleOutput)
            m_SupersampleOutput.Show(false);
        if (m_SupersampleItem)
            m_SupersampleItem.SetItem(null);
        if (m_SupersampleTexture)
            m_SupersampleTexture.Show(false);
    }

    protected void MovementLabUpdateSupersample(EntityAI item, int viewIndex, float width, float height, float fraction, float inset, float yInset)
    {
        if (!MovementLabPreviewQuality.Supersample)
        {
            MovementLabHideSupersample();
            m_Preview.Show(true);
            return;
        }
        if (!m_SupersampleTexture)
        {
            Widget sourceRoot = GetGame().GetWorkspace().CreateWidgets("MovementLabStartGate/GUI/MovementLabSupersample.layout");
            m_SupersampleTexture = RTTextureWidget.Cast(sourceRoot);
            if (m_SupersampleTexture)
            {
                m_SupersampleTexture.SetFlags(WidgetFlags.RENDER_ALWAYS | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS);
                m_SupersampleItem = ItemPreviewWidget.Cast(m_SupersampleTexture.FindAnyWidget("MovementLabHighResolutionItem"));
                if (m_SupersampleItem)
                    m_SupersampleItem.SetFlags(WidgetFlags.RENDER_ALWAYS | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS);
            }
        }
        if (!m_SupersampleOutput)
        {
            int outputFlags = WidgetFlags.VISIBLE | WidgetFlags.HEXACTPOS | WidgetFlags.VEXACTPOS | WidgetFlags.HEXACTSIZE | WidgetFlags.VEXACTSIZE | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS | WidgetFlags.STRETCH | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND;
            m_SupersampleOutput = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, width * fraction, height * fraction, outputFlags, 0xFFFFFFFF, 1, m_Root));
        }
        if (!m_SupersampleTexture || !m_SupersampleItem || !m_SupersampleOutput)
        {
            m_Preview.Show(true);
            return;
        }
        float renderWidth = Math.Clamp(Math.Ceil(width * fraction * 4), 4, 2048);
        float renderHeight = Math.Clamp(Math.Ceil(height * fraction * 4), 4, 1024);
        bool resize = renderWidth != m_SupersampleLastWidth || renderHeight != m_SupersampleLastHeight;
        m_SupersampleTexture.SetScreenPos(-3000, 0);
        m_SupersampleTexture.SetScreenSize(renderWidth, renderHeight);
        m_SupersampleTexture.Show(true);
        m_SupersampleItem.Show(true);
        if (m_SupersampleItem.GetItem() != item || resize)
        {
            m_SupersampleItem.SetItem(item);
            m_SupersampleItem.SetModelPosition("0 0 0");
            m_SupersampleItem.SetModelOrientation("0 0 0");
            m_SupersampleItem.SetView(viewIndex);
        }
        m_SupersampleLastWidth = renderWidth;
        m_SupersampleLastHeight = renderHeight;
        m_SupersampleOutput.SetImageTexture(0, m_SupersampleTexture);
        if (!m_SupersampleOutput.SetImage(0))
        {
            m_SupersampleOutput.Show(false);
            m_Preview.Show(true);
            return;
        }
        m_SupersampleOutput.ClearFlags(WidgetFlags.NOFILTER);
        m_SupersampleOutput.SetPos(width * inset, height * yInset);
        m_SupersampleOutput.SetSize(width * fraction, height * fraction);
        m_SupersampleOutput.Show(true);
        m_Preview.Show(false);
        if (!m_SupersampleReported)
        {
            Print("[MovementLab preview supersampling v36] RTTexture bound, requested render size=" + renderWidth + "x" + renderHeight + "; native pixel output still needs visual verification. F5 compares.");
            m_SupersampleReported = true;
        }
    }

}
