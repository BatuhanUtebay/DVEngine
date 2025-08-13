# dvge/ui/panels/player_panel.py

"""Player panel for managing player stats and inventory."""

from tkinter import messagebox
import customtkinter as ctk
from ...constants import *
from ..widgets.custom_widgets import ScrollableListFrame


class PlayerPanel:
    """Handles the Player tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_rowconfigure(4, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the player panel."""
        # Player Stats section
        ctk.CTkLabel(
            self.parent, text="Player Stats", font=FONT_PROPERTIES_LABEL
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.player_stats_frame = ScrollableListFrame(self.parent)
        self.player_stats_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkButton(
            self.parent, text="+ Add Stat", command=self._add_player_stat
        ).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # Starting Inventory section
        ctk.CTkLabel(
            self.parent, text="Starting Inventory", font=FONT_PROPERTIES_LABEL
        ).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.player_inventory_frame = ScrollableListFrame(self.parent)
        self.player_inventory_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkButton(
            self.parent, text="+ Add Item", command=self._add_inventory_item
        ).grid(row=5, column=0, padx=10, pady=10, sticky="ew")

    def update_panel(self):
        """Updates the panel with current data."""
        self._update_player_stats()
        self._update_player_inventory()

    def _update_player_stats(self):
        """Updates the player stats display."""
        self.player_stats_frame.clear_all()
        
        for stat, value in self.app.player_stats.items():
            item_frame = self.player_stats_frame.add_item_frame()
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Stat name entry
            name_entry = ctk.CTkEntry(item_frame)
            name_entry.insert(0, stat)
            name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            name_entry.bind(
                "<KeyRelease>", 
                lambda e, old_name=stat, w=name_entry: self._rename_player_stat(old_name, w.get())
            )
            
            # Stat value entry
            val_entry = ctk.CTkEntry(item_frame, width=80)
            val_entry.insert(0, str(value))
            val_entry.grid(row=0, column=1, padx=5, pady=5)
            val_entry.bind(
                "<KeyRelease>", 
                lambda e, name=stat, w=val_entry: self._change_stat_default(name, w.get())
            )
            
            # Delete button
            ctk.CTkButton(
                item_frame, text="✕", width=28, height=28, 
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda s=stat: self._delete_player_stat(s)
            ).grid(row=0, column=2, padx=5, pady=5)

    def _update_player_inventory(self):
        """Updates the player inventory display."""
        self.player_inventory_frame.clear_all()
        
        for i, item in enumerate(self.app.player_inventory):
            item_frame = self.player_inventory_frame.add_item_frame()
            item_frame.grid_columnconfigure(0, weight=1)
            
            # Item name entry
            name_entry = ctk.CTkEntry(item_frame, placeholder_text="Item Name")
            name_entry.insert(0, item.get("name", ""))
            name_entry.grid(row=0, column=0, padx=5, pady=(5,2), sticky="ew")
            name_entry.bind(
                "<KeyRelease>", 
                lambda e, idx=i, w=name_entry: self._update_inventory_item(idx, 'name', w.get())
            )
            
            # Item description entry
            desc_entry = ctk.CTkEntry(item_frame, placeholder_text="Item Description")
            desc_entry.insert(0, item.get("description", ""))
            desc_entry.grid(row=1, column=0, padx=5, pady=(2,5), sticky="ew")
            desc_entry.bind(
                "<KeyRelease>", 
                lambda e, idx=i, w=desc_entry: self._update_inventory_item(idx, 'description', w.get())
            )
            
            # Delete button
            ctk.CTkButton(
                item_frame, text="✕", width=28, height=28, 
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda idx=i: self._delete_inventory_item(idx)
            ).grid(row=0, rowspan=2, column=1, padx=5, pady=5)

    def _add_player_stat(self):
        """Adds a new player stat."""
        self.app._save_state_for_undo("Add Stat")
        new_stat_name = f"new_stat_{len(self.app.player_stats)}"
        self.app.player_stats[new_stat_name] = 10
        self.update_panel()

    def _rename_player_stat(self, old_name, new_name):
        """Renames a player stat."""
        if not new_name or (new_name in self.app.player_stats and new_name != old_name):
            return
        
        self.app._save_state_for_undo("Rename Stat")
        self.app.player_stats[new_name] = self.app.player_stats.pop(old_name)

    def _change_stat_default(self, name, value_str):
        """Changes the default value of a stat."""
        try:
            value = int(value_str)
        except (ValueError, KeyError):
            return
        
        if name in self.app.player_stats and self.app.player_stats[name] != value:
            self.app._save_state_for_undo("Change Stat Default")
            self.app.player_stats[name] = value

    def _delete_player_stat(self, stat_name):
        """Deletes a player stat."""
        if messagebox.askyesno("Delete Stat", f"Delete '{stat_name}'? This cannot be undone easily."):
            self.app._save_state_for_undo("Delete Stat")
            self.app.player_stats.pop(stat_name, None)
            self.update_panel()

    def _add_inventory_item(self):
        """Adds a new inventory item."""
        self.app._save_state_for_undo("Add Item")
        self.app.player_inventory.append({
            "name": f"new_item_{len(self.app.player_inventory)}", 
            "description": "A new item."
        })
        self.update_panel()
        
    def _update_inventory_item(self, index, key, value):
        """Updates an inventory item property."""
        if index < len(self.app.player_inventory):
            self.app._save_state_for_undo("Update Item")
            self.app.player_inventory[index][key] = value

    def _delete_inventory_item(self, index):
        """Deletes an inventory item."""
        if index < len(self.app.player_inventory):
            item_name = self.app.player_inventory[index]['name']
            if messagebox.askyesno("Delete Item", f"Delete '{item_name}'?"):
                self.app._save_state_for_undo("Delete Item")
                del self.app.player_inventory[index]
                self.update_panel()