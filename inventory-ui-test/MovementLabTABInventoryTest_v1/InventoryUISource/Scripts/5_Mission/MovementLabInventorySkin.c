#ifndef SERVER
// Appearance-only layer over DayZ's native inventory controls.
// Never writes inventory locations, cargo size, item quantities or player state.
class MovementLabInventorySkin
{
    static ImageWidget Background(Widget parent, string name, string texture, int sort = -20)
    {
        if (!parent)
            return null;
        ImageWidget image = ImageWidget.Cast(parent.FindAnyWidget(name));
        if (image)
            return image;
        WidgetFlags flags = WidgetFlags.VISIBLE | WidgetFlags.STRETCH;
        flags = flags | WidgetFlags.SOURCEALPHA | WidgetFlags.BLEND;
        flags = flags | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
        image = ImageWidget.Cast(GetGame().GetWorkspace().CreateWidget(ImageWidgetTypeID, 0, 0, 1, 1, flags, 0xFFFFFFFF, sort, parent));
        if (!image)
            return null;
        image.SetName(name);
        if (!image.LoadImageFile(0, "MovementLabInventoryUI/GUI/Textures/" + texture))
        {
            image.Show(false);
            Print("[MovementLab TAB] Texture unavailable: " + texture);
            return null;
        }
        image.SetImage(0);
        return image;
    }

    static TextWidget Label(Widget parent, string name, float x, float y, float width, float height)
    {
        if (!parent)
            return null;
        TextWidget label = TextWidget.Cast(parent.FindAnyWidget(name));
        if (!label)
        {
            WidgetFlags flags = WidgetFlags.VISIBLE | WidgetFlags.IGNOREPOINTER | WidgetFlags.NOFOCUS;
            flags = flags | WidgetFlags.EXACTPOS | WidgetFlags.EXACTSIZE | WidgetFlags.NOWRAP;
            label = TextWidget.Cast(GetGame().GetWorkspace().CreateWidget(TextWidgetTypeID, x, y, width, height, flags, 0xFFFFFFFF, 10, parent));
            if (!label)
                return null;
            label.SetName(name);
            label.SetTextExactSize(11);
            label.SetColor(ARGB(255, 205, 205, 201));
        }
        label.SetPos(x, y);
        label.SetSize(width, height);
        return label;
    }

    static string FitName(string name, float width)
    {
        string translated = Widget.TranslateString(name);
        int count = Math.Floor(width / 6);
        count = Math.Clamp(count, 5, 48);
        if (translated.Length() > count)
            return translated.Substring(0, count - 3) + "...";
        return translated;
    }

    static string Section(EntityAI item)
    {
        PlayerBase player = PlayerBase.Cast(GetGame().GetPlayer());
        if (player && item)
        {
            if (player.FindAttachmentBySlotName("Vest") == item)
                return "Chest Rig";
            if (player.FindAttachmentBySlotName("Back") == item)
                return "Backpack";
            if (player.FindAttachmentBySlotName("Legs") == item)
                return "Pockets";
        }
        if (item)
            return Widget.TranslateString(item.GetDisplayName());
        return "";
    }
}

modded class CargoContainerRow
{
    void CargoContainerRow(LayoutHolder parent)
    {
        #ifndef PLATFORM_CONSOLE
        for (int themeColumn = 0; themeColumn < m_MaxColumns; themeColumn++)
        {
            Widget themeCell = GetMainWidget().FindAnyWidget("Icon" + themeColumn);
            MovementLabInventorySkin.Background(themeCell, "MovementLabCell", "cell.paa");
        }
        #endif
    }
}

modded class Icon
{
    protected TextWidget m_MovementLabItemName;
    protected float m_MovementLabItemWidth;
    protected EntityAI m_MovementLabNamedItem;

    void Icon(LayoutHolder parent, bool hands_icon = false)
    {
        #ifndef PLATFORM_CONSOLE
        if (CargoContainer.Cast(parent) || HandsPreview.Cast(parent))
        {
            MovementLabInventorySkin.Background(GetRootWidget(), "MovementLabItemBorder", "cell.paa");
            m_MovementLabItemName = MovementLabInventorySkin.Label(GetRootWidget(), "MovementLabItemName", 3, 1, 30, 14);
            if (m_QuantityItem)
                m_QuantityItem.SetTextExactSize(12);
        }
        #endif
    }

    override void UpdateInterval()
    {
        super.UpdateInterval();
        if (!m_MovementLabItemName || !GetRootWidget())
            return;
        float itemWidth;
        float itemHeight;
        GetRootWidget().GetScreenSize(itemWidth, itemHeight);
        m_MovementLabItemName.Show(m_Obj && !m_IsDragged);
        if (!m_Obj)
            return;
        if (m_QuantityItem && m_Obj.IsMagazine() && !m_Obj.IsAmmoPile())
            m_QuantityItem.SetText(QuantityConversions.GetItemQuantityText(m_Obj, true));
        if (m_MovementLabNamedItem != m_Obj || Math.AbsFloat(itemWidth - m_MovementLabItemWidth) > 0.5)
        {
            m_MovementLabNamedItem = m_Obj;
            m_MovementLabItemWidth = itemWidth;
            m_MovementLabItemName.SetSize(Math.Max(10, itemWidth - 6), 14);
            m_MovementLabItemName.SetText(MovementLabInventorySkin.FitName(m_Obj.GetDisplayName(), itemWidth - 6));
        }
    }
}

modded class ClosableHeader
{
    void ClosableHeader(LayoutHolder parent, string function_name)
    {
        #ifndef PLATFORM_CONSOLE
        MovementLabInventorySkin.Background(m_PanelWidget, "MovementLabHeaderBackground", "header.paa");
        m_DefaultColor = ARGB(255, 28, 28, 28);
        if (m_PanelWidget)
            m_PanelWidget.SetColor(m_DefaultColor);
        m_DefaultFontSize = 14;
        if (m_HeaderText)
        {
            m_HeaderText.SetTextExactSize(14);
            m_HeaderText.SetColor(ARGB(255, 204, 204, 200));
        }
        #endif
    }

    override void SetName(string name)
    {
        super.SetName(name);
        #ifndef PLATFORM_CONSOLE
        if (m_HeaderText)
        {
            m_HeaderText.SetText(name);
            m_HeaderText.SetTextExactSize(14);
        }
        #endif
    }
}

modded class CargoContainer
{
    protected bool m_MovementLabSidebar;
    protected Widget m_MovementLabGearColumn;
    protected ItemPreviewWidget m_MovementLabGearPreview;
    protected TextWidget m_MovementLabGearName;
    protected TextWidget m_MovementLabGearCapacity;
    protected int m_MovementLabLastCapacity = -1;
    protected int m_MovementLabLastMaxCapacity = -1;
    protected EntityAI m_MovementLabBoundGear;
    protected int m_MovementLabBoundView = -1;
    protected float m_MovementLabSidebarWidth;

    protected bool MovementLabPrepareSidebar(EntityAI item)
    {
        #ifdef PLATFORM_CONSOLE
        return false;
        #else
        if (m_MovementLabSidebar)
            return true;
        if (!item || !m_RootWidget || !m_RootWidget.GetParent())
            return false;
        if (item.GetHierarchyRootPlayer() != GetGame().GetPlayer())
            return false;
        Widget parent = m_RootWidget.GetParent();
        parent.Update();
        float parentWidth;
        float parentHeight;
        parent.GetScreenSize(parentWidth, parentHeight);
        if (parentWidth < 300)
            return false;
        float oldX;
        float oldY;
        float oldWidth;
        float oldHeight;
        m_RootWidget.GetPos(oldX, oldY);
        m_RootWidget.GetSize(oldWidth, oldHeight);
        int oldFlags = m_RootWidget.GetFlags();
        // Preserve native units: SizeToChild/SizeToParent assume these flags.
        float insetX = 0.22;
        float insetWidth = 0.78;
        if (oldFlags & WidgetFlags.HEXACTPOS)
            insetX = parentWidth * 0.22;
        if (oldFlags & WidgetFlags.HEXACTSIZE)
            insetWidth = parentWidth * 0.78;
        m_RootWidget.SetPos(insetX, oldY);
        m_RootWidget.SetSize(insetWidth, oldHeight);
        m_RootWidget.Update();
        float parentX;
        float parentY;
        float gridX;
        float gridY;
        parent.GetScreenPos(parentX, parentY);
        m_RootWidget.GetScreenPos(gridX, gridY);
        // Some native spacers own positions. Do not force a misaligned sidecar.
        if (gridX - parentX < parentWidth * 0.10)
        {
            m_RootWidget.SetPos(oldX, oldY);
            m_RootWidget.SetSize(oldWidth, oldHeight);
            Print("[MovementLab TAB] Native spacer owns cargo position; using themed native geometry.");
            return false;
        }
        m_MovementLabSidebarWidth = parentWidth * 0.22 - 8;
        m_RootWidget.ClearFlags(WidgetFlags.CLIPCHILDREN);
        Print("[MovementLab TAB] Sidebar geometry prepared before native cargo initialization.");
        return true;
        #endif
    }

    override void SetEntity(EntityAI item, int cargo_index = 0, bool immedUpdate = true)
    {
        m_MovementLabSidebar = MovementLabPrepareSidebar(item);
        // Native code measures the actual row cells AFTER the whole-grid inset.
        super.SetEntity(item, cargo_index, immedUpdate);
        if (m_MovementLabSidebar)
        {
            MovementLabCreateGearColumn();
            MovementLabUpdateGearColumn();
        }
    }

    protected void MovementLabCreateGearColumn()
    {
        if (m_MovementLabGearColumn || !m_Entity)
            return;
        WidgetFlags flags = WidgetFlags.VISIBLE | WidgetFlags.EXACTPOS | WidgetFlags.EXACTSIZE | WidgetFlags.NOFOCUS;
        m_MovementLabGearColumn = GetGame().GetWorkspace().CreateWidgets("MovementLabInventoryUI/GUI/GearColumn.layout", m_RootWidget);
        if (!m_MovementLabGearColumn)
            return;
        m_MovementLabGearColumn.SetName("MovementLabGearColumn");
        m_MovementLabGearColumn.SetFlags(flags);
        m_MovementLabGearColumn.SetPos(-m_MovementLabSidebarWidth - 8, 0);
        m_MovementLabGearColumn.SetSize(m_MovementLabSidebarWidth, 100);
        MovementLabInventorySkin.Background(m_MovementLabGearColumn, "MovementLabGearBorder", "cell.paa");
        m_MovementLabGearName = MovementLabInventorySkin.Label(m_MovementLabGearColumn, "MovementLabGearName", 3, 1, m_MovementLabSidebarWidth - 6, 14);
        m_MovementLabGearCapacity = MovementLabInventorySkin.Label(m_MovementLabGearColumn, "MovementLabGearCapacity", 3, 84, m_MovementLabSidebarWidth - 6, 15);
        if (m_MovementLabGearCapacity)
            m_MovementLabGearCapacity.SetColor(ARGB(255, 195, 204, 174));
        m_MovementLabGearPreview = ItemPreviewWidget.Cast(m_MovementLabGearColumn.FindAnyWidget("MovementLabGearPreview"));
        if (m_MovementLabGearPreview)
        {
            m_MovementLabGearPreview.SetName("MovementLabGearPreview");
            m_MovementLabGearPreview.SetPos(2, 15);
            m_MovementLabGearPreview.SetSize(m_MovementLabSidebarWidth - 4, 66);
            Container owner = Container.Cast(GetParent());
            if (owner && ClosableHeader.Cast(owner.GetHeader()))
            {
                ClosableHeader header = ClosableHeader.Cast(owner.GetHeader());
                WidgetEventHandler.GetInstance().RegisterOnDrag(m_MovementLabGearPreview, header, "OnDragHeader");
                WidgetEventHandler.GetInstance().RegisterOnDrop(m_MovementLabGearPreview, header, "OnDropHeader");
                WidgetEventHandler.GetInstance().RegisterOnMouseEnter(m_MovementLabGearPreview, header, "MouseEnter");
                WidgetEventHandler.GetInstance().RegisterOnMouseLeave(m_MovementLabGearPreview, header, "MouseLeave");
                WidgetEventHandler.GetInstance().RegisterOnDraggingOver(m_MovementLabGearPreview, header, "DraggingOverHeader");
                WidgetEventHandler.GetInstance().RegisterOnDropReceived(m_MovementLabGearPreview, owner, "OnDropReceivedFromHeader");
            }
        }
    }

    protected void MovementLabUpdateGearColumn()
    {
        if (!m_MovementLabGearColumn || !m_Entity || !m_Cargo || !m_MovementLabGearPreview)
            return;
        float gridWidth;
        float gridHeight;
        m_RootWidget.GetScreenSize(gridWidth, gridHeight);
        float columnHeight = Math.Min(126, gridHeight);
        if (columnHeight < 44)
        {
            m_MovementLabGearColumn.Show(false);
            return;
        }
        m_MovementLabGearColumn.Show(true);
        Container cargoOwner = Container.Cast(GetParent());
        if (cargoOwner && cargoOwner.GetHeader())
        {
            Widget headerPreview = cargoOwner.GetHeader().GetMainWidget().FindAnyWidget("Render");
            if (headerPreview)
                headerPreview.Show(false);
        }
        m_MovementLabGearColumn.SetSize(m_MovementLabSidebarWidth, columnHeight);
        m_MovementLabGearPreview.SetSize(m_MovementLabSidebarWidth - 4, columnHeight - 32);
        int previewView = m_Entity.GetViewIndex();
        if (m_MovementLabBoundGear != m_Entity || m_MovementLabBoundView != previewView)
        {
            m_MovementLabGearPreview.SetItem(m_Entity);
            m_MovementLabGearPreview.SetView(previewView);
            m_MovementLabBoundGear = m_Entity;
            m_MovementLabBoundView = previewView;
            if (m_MovementLabGearName)
                m_MovementLabGearName.SetText(MovementLabInventorySkin.FitName(m_Entity.GetDisplayName(), m_MovementLabSidebarWidth - 6));
        }
        int occupied = GetCargoCapacity();
        int maximum = GetMaxCargoCapacity();
        if (m_MovementLabGearCapacity)
        {
            m_MovementLabGearCapacity.SetPos(3, columnHeight - 16);
            if (occupied != m_MovementLabLastCapacity || maximum != m_MovementLabLastMaxCapacity)
            {
                m_MovementLabGearCapacity.SetText("" + occupied + " / " + maximum);
                m_MovementLabLastCapacity = occupied;
                m_MovementLabLastMaxCapacity = maximum;
            }
        }
    }

    override void UpdateHeaderText()
    {
        super.UpdateHeaderText();
        #ifndef PLATFORM_CONSOLE
        if (m_MovementLabSidebar && m_Entity)
        {
            Container owner = Container.Cast(GetParent());
            if (owner && owner.GetHeader())
                owner.GetHeader().SetName(MovementLabInventorySkin.Section(m_Entity));
        }
        #endif
    }

    override void UpdateInterval()
    {
        super.UpdateInterval();
        if (m_MovementLabSidebar)
            MovementLabUpdateGearColumn();
    }
}
#endif
