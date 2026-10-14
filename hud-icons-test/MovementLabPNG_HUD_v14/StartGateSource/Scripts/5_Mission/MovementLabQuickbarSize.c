// HUD quickbar only; native bindings and item controller remain unchanged.
modded class InventoryQuickbar
{
    protected ref map<Widget, vector> m_MovementLabQuickbarSizes = new map<Widget, vector>();
    protected ref map<Widget, vector> m_MovementLabQuickbarPositions = new map<Widget, vector>();
    protected float m_MovementLabQuickbarBottom;
    protected bool m_MovementLabQuickbarMeasured;

    override void UpdateItems(Widget quickbarGridWidget)
    {
        super.UpdateItems(quickbarGridWidget);
        if (!quickbarGridWidget || quickbarGridWidget.GetName() != "QuickbarGrid")
            return;
        // Constructor calls UpdateItems before subclass field initializers on some builds.
        if (!m_MovementLabQuickbarSizes)
            m_MovementLabQuickbarSizes = new map<Widget, vector>();
        if (!m_MovementLabQuickbarPositions)
            m_MovementLabQuickbarPositions = new map<Widget, vector>();
        float barX;
        float barY;
        float barW;
        float barH;
        quickbarGridWidget.GetScreenPos(barX, barY);
        quickbarGridWidget.GetScreenSize(barW, barH);
        if (!m_MovementLabQuickbarMeasured)
        {
            m_MovementLabQuickbarBottom = barY + barH;
            m_MovementLabQuickbarMeasured = true;
        }
        MovementLabScaleQuickbarChildren(quickbarGridWidget);
        if (m_Grid)
        {
            for (int previewSlotIndex = 0; previewSlotIndex < m_Grid.GetGridSize(); previewSlotIndex++)
                MovementLabUpdateSlotPreview(previewSlotIndex);
        }
        // Native layouts recalculate their contents when slot count changes.
        quickbarGridWidget.GetScreenSize(barW, barH);
        Widget barParent = quickbarGridWidget.GetParent();
        if (barParent)
        {
            float parentX;
            float parentY;
            float parentW;
            float parentH;
            barParent.GetScreenPos(parentX, parentY);
            barParent.GetScreenSize(parentW, parentH);
            quickbarGridWidget.SetScreenPos(parentX + (parentW - barW) * 0.5, m_MovementLabQuickbarBottom - barH);
        }
    }

    protected void MovementLabScaleQuickbarChildren(Widget parent)
    {
        Widget slotWidget = parent.GetChildren();
        while (slotWidget)
        {
            // Leave native item-wrapper layout intact; it already fills its enlarged slot.
            if (slotWidget.GetName() == "GridItemBck" || slotWidget.GetName() == "MovementLabQuickbarPreviewRoot")
            {
                slotWidget = slotWidget.GetSibling();
                continue;
            }
            int slotFlags = slotWidget.GetFlags();
            float slotW;
            float slotH;
            float slotX;
            float slotY;
            slotWidget.GetSize(slotW, slotH);
            slotWidget.GetPos(slotX, slotY);
            if (!m_MovementLabQuickbarSizes.Contains(slotWidget))
            {
                m_MovementLabQuickbarSizes.Insert(slotWidget, Vector(slotW, slotH, 0));
                m_MovementLabQuickbarPositions.Insert(slotWidget, Vector(slotX, slotY, 0));
            }
            vector originalSize = m_MovementLabQuickbarSizes.Get(slotWidget);
            vector originalPosition = m_MovementLabQuickbarPositions.Get(slotWidget);
            if ((slotFlags & WidgetFlags.HEXACTSIZE) != 0)
                slotW = originalSize[0] * 1.5;
            if ((slotFlags & WidgetFlags.VEXACTSIZE) != 0)
                slotH = originalSize[1] * 1.5;
            slotWidget.SetSize(slotW, slotH);
            if ((slotFlags & WidgetFlags.HEXACTPOS) != 0)
                slotX = originalPosition[0] * 1.5;
            if ((slotFlags & WidgetFlags.VEXACTPOS) != 0)
                slotY = originalPosition[1] * 1.5;
            slotWidget.SetPos(slotX, slotY);
            MovementLabScaleQuickbarChildren(slotWidget);
            slotWidget = slotWidget.GetSibling();
        }
    }
    protected void MovementLabUpdateSlotPreview(int index)
    {
        Widget slot = m_Grid.GetItemBackground(index);
        if (!slot)
            return;
        Widget previewRoot = slot.FindAnyWidget("MovementLabQuickbarPreviewRoot");
        Widget nativeItemRoot = m_Grid.GetItem(index);
        ItemPreviewWidget nativePreview;
        if (nativeItemRoot)
            nativePreview = ItemPreviewWidget.Cast(nativeItemRoot.FindAnyWidget("Preview"));
        EntityAI item;
        if (nativePreview)
        {
            item = nativePreview.GetItem();
            nativePreview.Show(false);
        }
        if (!previewRoot)
            previewRoot = GetGame().GetWorkspace().CreateWidgets("MovementLabStartGate/GUI/MovementLabQuickbarPreview.layout", slot);
        if (previewRoot)
            MovementLabUpdateCard(slot, previewRoot, item);
        if (!item)
        {
            if (previewRoot)
            {
                ItemPreviewWidget emptyPreview = ItemPreviewWidget.Cast(previewRoot.FindAnyWidget("MovementLabSlotRender"));
                if (emptyPreview)
                    emptyPreview.SetItem(null);
                previewRoot.Show(true);
            }
            return;
        }
        if (!previewRoot)
            previewRoot = GetGame().GetWorkspace().CreateWidgets("MovementLabStartGate/GUI/MovementLabQuickbarPreview.layout", slot);
        if (!previewRoot)
            return;
        ItemPreviewWidget slotPreview = ItemPreviewWidget.Cast(previewRoot.FindAnyWidget("MovementLabSlotRender"));
        if (!slotPreview)
            return;
        // Fresh layout has explicit top-left anchors and no native item-wrapper offsets.
        previewRoot.Show(true);
        float previewFraction = 0.60;
        if (item.IsWeapon())
        {
            previewFraction = 0.88;
            if (GetGame().IsKindOf(item.GetType(), "Pistol_Base"))
                previewFraction = 0.70;
        }
        float previewInset = (1 - previewFraction) * 0.5;
        slotPreview.SetPos(previewInset, previewInset);
        slotPreview.SetSize(previewFraction, previewFraction);
        if (slotPreview.GetItem() != item)
        {
            slotPreview.SetItem(item);
            slotPreview.SetModelPosition("0 0 0");
            slotPreview.SetModelOrientation("0 0 0");
            slotPreview.SetView(item.GetViewIndex());
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
                image.LoadImageFile(0, "MovementLabStartGate/GUI/Textures/solid.paa");
                image.SetImage(0);
            }
            TextWidget text = TextWidget.Cast(result);
            if (text)
            {
                result.SetSort(2);
                text.SetBold(true);
                text.SetTextExactSize(9);
                text.SetOutline(1, 0xCC000000);
                text.SetShadow(2, 0xFF000000, 0.8, 0, 0);
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
        float width;
        float height;
        slot.GetScreenSize(width, height);
        slot.ClearFlags(WidgetFlags.CLIPCHILDREN);
        root.ClearFlags(WidgetFlags.CLIPCHILDREN);
        MovementLabCardWidget(root, "MLCardBackground", ImageWidgetTypeID, 0, 0, width, height, 0x70383838);
        MovementLabCardWidget(root, "MLCardTop", ImageWidgetTypeID, 0, 0, width, 1, 0xFF101010);
        MovementLabCardWidget(root, "MLCardBottom", ImageWidgetTypeID, 0, height - 1, width, 1, 0xFF101010);
        MovementLabCardWidget(root, "MLCardLeft", ImageWidgetTypeID, 0, 0, 1, height, 0xFF101010);
        MovementLabCardWidget(root, "MLCardRight", ImageWidgetTypeID, width - 1, 0, 1, height, 0xFF101010);
        TextWidget name = TextWidget.Cast(MovementLabCardWidget(root, "MLCardName", TextWidgetTypeID, 3, -16, width * 0.68, 14, 0xFFFFFFFF));
        TextWidget calibre = TextWidget.Cast(MovementLabCardWidget(root, "MLCardCalibre", TextWidgetTypeID, width * 0.68, -16, width * 0.30, 14, 0xFFFFFFFF));
        TextWidget fireMode = TextWidget.Cast(MovementLabCardWidget(root, "MLCardMode", TextWidgetTypeID, 3, height - 14, width * 0.48, 13, 0xFFFFFFFF));
        TextWidget rounds = TextWidget.Cast(MovementLabCardWidget(root, "MLCardRounds", TextWidgetTypeID, width * 0.55, height - 14, width * 0.4, 13, 0xFFFFFFFF));
        Widget health = MovementLabCardWidget(root, "MLCardHealth", ImageWidgetTypeID, width - 4, 0, 3, height, 0xFF40FF00);
        Weapon firearm = Weapon.Cast(item);
        if (name)
        {
            string title = "";
            if (item)
                title = item.GetDisplayName();
            title.ToUpper();
            int limit = Math.Max(6, Math.Floor(width * 0.68 / 6));
            if (title.Length() > limit)
                title = title.Substring(0, limit - 1) + "…";
            name.SetText(title);
        }
        if (calibre)
        {
            calibre.Show(firearm != null);
            if (firearm)
                calibre.SetText(MovementLabCalibre(item));
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
            string mode = "SINGLE";
            if (firearm.GetCurrentModeAutoFire(muzzle))
                mode = "AUTO";
            else if (firearm.GetCurrentModeBurstSize(muzzle) > 1)
                mode = "BURST";
            if (fireMode)
                fireMode.SetText(mode);
            int count = 0;
            Magazine magazine = firearm.GetMagazine(muzzle);
            if (magazine)
                count = magazine.GetAmmoCount();
            if (!firearm.IsChamberEmpty(muzzle) && !firearm.IsChamberFiredOut(muzzle))
                count = count + 1;
            if (rounds)
                rounds.SetText(count.ToString());
        }
    }

}
