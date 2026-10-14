// Resize slot containers once; explicitly centre previews without recursively scaling children.
modded class InventoryQuickbar
{
    protected float m_MovementLabSlotWidth;
    protected float m_MovementLabSlotHeight;
    protected float m_MovementLabSlotGap;
    protected float m_MovementLabBarBottom;

    override void UpdateItems(Widget quickbarGridWidget)
    {
        super.UpdateItems(quickbarGridWidget);
        if (!quickbarGridWidget || quickbarGridWidget.GetName() != "QuickbarGrid" || !m_Grid)
            return;
        Widget firstSlot = m_Grid.GetItemBackground(0);
        if (!firstSlot)
            return;
        if (m_MovementLabSlotWidth <= 0)
        {
            float firstX;
            float firstY;
            float firstW;
            float firstH;
            firstSlot.GetScreenPos(firstX, firstY);
            firstSlot.GetScreenSize(firstW, firstH);
            m_MovementLabSlotWidth = firstW * 1.5;
            m_MovementLabSlotHeight = firstH * 1.5;
            m_MovementLabBarBottom = firstY + firstH;
            Widget secondSlot = m_Grid.GetItemBackground(1);
            if (secondSlot)
            {
                float secondX;
                float secondY;
                secondSlot.GetScreenPos(secondX, secondY);
                m_MovementLabSlotGap = Math.Max(0, secondX - firstX - firstW) * 1.5;
            }
        }
        int slotCount = m_Grid.GetGridSize();
        if (slotCount <= 0)
            return;
        float totalWidth = slotCount * m_MovementLabSlotWidth + (slotCount - 1) * m_MovementLabSlotGap;
        Widget barParent = quickbarGridWidget.GetParent();
        if (!barParent)
            return;
        float parentX;
        float parentY;
        float parentW;
        float parentH;
        barParent.GetScreenPos(parentX, parentY);
        barParent.GetScreenSize(parentW, parentH);
        float barLeft = parentX + (parentW - totalWidth) * 0.5;
        float barTop = m_MovementLabBarBottom - m_MovementLabSlotHeight;
        quickbarGridWidget.SetScreenSize(totalWidth, m_MovementLabSlotHeight);
        quickbarGridWidget.SetScreenPos(barLeft, barTop);
        for (int slotIndex = 0; slotIndex < slotCount; slotIndex++)
        {
            Widget slot = m_Grid.GetItemBackground(slotIndex);
            if (!slot)
                continue;
            float slotLeft = barLeft + slotIndex * (m_MovementLabSlotWidth + m_MovementLabSlotGap);
            slot.SetScreenSize(m_MovementLabSlotWidth, m_MovementLabSlotHeight);
            slot.SetScreenPos(slotLeft, barTop);
            Widget itemRoot = m_Grid.GetItem(slotIndex);
            if (!itemRoot)
                continue;
            Widget itemBackground = slot.FindAnyWidget("GridItemBck");
            if (itemBackground)
            {
                itemBackground.SetScreenSize(m_MovementLabSlotWidth, m_MovementLabSlotHeight);
                itemBackground.SetScreenPos(slotLeft, barTop);
            }
            itemRoot.SetScreenSize(m_MovementLabSlotWidth, m_MovementLabSlotHeight);
            itemRoot.SetScreenPos(slotLeft, barTop);
            ItemPreviewWidget preview = ItemPreviewWidget.Cast(itemRoot.FindAnyWidget("Preview"));
            if (!preview)
                continue;
            // Keep small inventory objects smaller instead of filling the entire enlarged slot.
            float previewFraction = 0.60;
            EntityAI previewItem = preview.GetItem();
            if (previewItem && previewItem.IsWeapon())
                previewFraction = 0.88;
            float previewW = m_MovementLabSlotWidth * previewFraction;
            float previewH = m_MovementLabSlotHeight * previewFraction;
            preview.SetScreenSize(previewW, previewH);
            preview.SetScreenPos(slotLeft + (m_MovementLabSlotWidth - previewW) * 0.5, barTop + (m_MovementLabSlotHeight - previewH) * 0.5);
        }
    }
}
