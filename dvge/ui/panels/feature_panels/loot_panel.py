import customtkinter as ctk
from ....constants import *
from ....features.loot_system import Rarity


class LootPanel(ctk.CTkFrame):
    """Panel for configuring loot tables and treasure chests."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_loot_table = None
        
        self._setup_layout()
        self._create_widgets()
        
    def _setup_layout(self):
        """Sets up the panel layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
    def _create_widgets(self):
        """Creates loot configuration widgets."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            title_frame, text="💎 Loot Table Configuration",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_WARNING
        ).pack(padx=10, pady=10)
        
        # Chest Settings
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        settings_frame.grid_columnconfigure((0,1), weight=1)
        
        # Lock settings
        lock_frame = ctk.CTkFrame(settings_frame, fg_color=COLOR_SECONDARY_FRAME)
        lock_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.is_locked = ctk.CTkCheckBox(
            lock_frame, text="Locked",
            font=FONT_PROPERTIES_ENTRY
        )
        self.is_locked.pack(side="left", padx=10, pady=5)
        
        self.lock_difficulty = ctk.CTkEntry(
            lock_frame, placeholder_text="Difficulty", width=80
        )
        self.lock_difficulty.pack(side="left", padx=5, pady=5)
        
        # Trap settings
        trap_frame = ctk.CTkFrame(settings_frame, fg_color=COLOR_SECONDARY_FRAME)
        trap_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        self.is_trapped = ctk.CTkCheckBox(
            trap_frame, text="Trapped",
            font=FONT_PROPERTIES_ENTRY
        )
        self.is_trapped.pack(side="left", padx=10, pady=5)
        
        self.trap_damage = ctk.CTkEntry(
            trap_frame, placeholder_text="Damage", width=80
        )
        self.trap_damage.pack(side="left", padx=5, pady=5)
        
        # Loot Items
        loot_container = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        loot_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        loot_container.grid_columnconfigure(0, weight=1)
        loot_container.grid_rowconfigure(1, weight=1)
        
        # Header with tabs
        tab_frame = ctk.CTkFrame(loot_container, fg_color="transparent")
        tab_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.items_btn = ctk.CTkButton(
            tab_frame, text="Items", width=80,
            command=lambda: self._switch_tab("items"),
            fg_color=COLOR_ACCENT
        )
        self.items_btn.pack(side="left", padx=2)
        
        self.currency_btn = ctk.CTkButton(
            tab_frame, text="Currency", width=80,
            command=lambda: self._switch_tab("currency")
        )
        self.currency_btn.pack(side="left", padx=2)
        
        # Content area
        self.content_frame = ctk.CTkScrollableFrame(loot_container)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Add button
        self.add_btn = ctk.CTkButton(
            loot_container, text="+ Add Item",
            command=self._add_loot_item, height=28
        )
        self.add_btn.grid(row=2, column=0, pady=5)
        
        self._show_items_content()
        
    def _switch_tab(self, tab):
        """Switches between items and currency tabs."""
        if tab == "items":
            self.items_btn.configure(fg_color=COLOR_ACCENT)
            self.currency_btn.configure(fg_color=COLOR_SECONDARY_FRAME)
            self._show_items_content()
        else:
            self.currency_btn.configure(fg_color=COLOR_ACCENT)
            self.items_btn.configure(fg_color=COLOR_SECONDARY_FRAME)
            self._show_currency_content()
            
    def _show_items_content(self):
        """Shows item loot configuration."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        self.add_btn.configure(text="+ Add Item")
        
    def _show_currency_content(self):
        """Shows currency configuration."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        currency_frame = ctk.CTkFrame(self.content_frame)
        currency_frame.pack(fill="x", pady=10, padx=10)
        currency_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            currency_frame, text="Gold Range:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        range_frame = ctk.CTkFrame(currency_frame, fg_color="transparent")
        range_frame.grid(row=0, column=1, sticky="ew")
        
        self.min_gold = ctk.CTkEntry(range_frame, placeholder_text="Min", width=80)
        self.min_gold.pack(side="left", padx=5)
        
        ctk.CTkLabel(range_frame, text="-").pack(side="left")
        
        self.max_gold = ctk.CTkEntry(range_frame, placeholder_text="Max", width=80)
        self.max_gold.pack(side="left", padx=5)
        
        self.add_btn.configure(text="Save Currency")
        
    def _add_loot_item(self):
        """Adds a new loot item row."""
        item_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_SECONDARY_FRAME)
        item_frame.pack(fill="x", pady=2)
        item_frame.grid_columnconfigure(0, weight=1)
        
        # Item name and description
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        name_entry = ctk.CTkEntry(info_frame, placeholder_text="Item name")
        name_entry.pack(fill="x", pady=2)
        
        desc_entry = ctk.CTkEntry(info_frame, placeholder_text="Description")
        desc_entry.pack(fill="x", pady=2)
        
        # Rarity selection
        rarity_combo = ctk.CTkComboBox(
            item_frame,
            values=["Common", "Uncommon", "Rare", "Epic", "Legendary"],
            width=120
        )
        rarity_combo.set("Common")
        rarity_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Remove button
        ctk.CTkButton(
            item_frame, text="✕", width=30, height=30,
            fg_color="transparent", hover_color=COLOR_ERROR,
            command=item_frame.destroy
        ).grid(row=0, column=2, padx=5, pady=5)