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
        if (!item)
        {
            if (previewRoot)
            {
                ItemPreviewWidget emptyPreview = ItemPreviewWidget.Cast(previewRoot.FindAnyWidget("MovementLabSlotRender"));
                if (emptyPreview)
                    emptyPreview.SetItem(null);
                previewRoot.Show(false);
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
            previewFraction = 0.70;
        float previewInset = (1 - previewFraction) * 0.5;
        slotPreview.SetPos(previewInset, previewInset + 0.20);
        slotPreview.SetSize(previewFraction, previewFraction);
        if (slotPreview.GetItem() != item)
        {
            slotPreview.SetItem(item);
            slotPreview.SetModelPosition("0 0 0");
            slotPreview.SetModelOrientation("0 0 0");
            slotPreview.SetView(item.GetViewIndex());
        }
    }
}
