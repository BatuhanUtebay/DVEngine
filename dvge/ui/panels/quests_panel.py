# dvge/ui/panels/quests_panel.py

"""Quests panel for managing quests and journal entries."""

from tkinter import messagebox
import customtkinter as ctk
from ...constants import *
from ...models import Quest
from ..widgets.custom_widgets import ScrollableListFrame


class QuestsPanel:
    """Handles the Quests tab in the properties panel."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the tab layout."""
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the quests panel."""
        # Main container
        main_frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # Scrollable quests frame
        self.quests_frame = ScrollableListFrame(
            main_frame,
            label_text="Quests / Journal",
            label_font=FONT_PROPERTIES_LABEL
        )
        self.quests_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add quest button
        ctk.CTkButton(
            main_frame, text="+ Add Quest", command=self._add_quest
        ).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    def update_panel(self):
        """Updates the panel with current data."""
        self.quests_frame.clear_all()
        
        for quest_id, quest in self.app.quests.items():
            item_frame = self.quests_frame.add_item_frame()
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Quest ID
            ctk.CTkLabel(
                item_frame, text="ID:", font=FONT_PROPERTIES_ENTRY
            ).grid(row=0, column=0, padx=5, pady=2, sticky="w")
            
            id_entry = ctk.CTkEntry(item_frame, font=FONT_PROPERTIES_ENTRY)
            id_entry.insert(0, quest.id)
            id_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
            id_entry.bind(
                "<KeyRelease>", 
                lambda e, old_id=quest_id, w=id_entry: self._rename_quest(old_id, w.get())
            )
            
            # Quest Name
            ctk.CTkLabel(
                item_frame, text="Name:", font=FONT_PROPERTIES_ENTRY
            ).grid(row=1, column=0, padx=5, pady=2, sticky="w")
            
            name_entry = ctk.CTkEntry(item_frame, font=FONT_PROPERTIES_ENTRY)
            name_entry.insert(0, quest.name)
            name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
            name_entry.bind(
                "<KeyRelease>", 
                lambda e, qid=quest.id, w=name_entry: self._update_quest_prop(qid, 'name', w.get())
            )
            
            # Quest Description
            ctk.CTkLabel(
                item_frame, text="Desc:", font=FONT_PROPERTIES_ENTRY
            ).grid(row=2, column=0, padx=5, pady=2, sticky="w")
            
            desc_entry = ctk.CTkEntry(item_frame, font=FONT_PROPERTIES_ENTRY)
            desc_entry.insert(0, quest.description)
            desc_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
            desc_entry.bind(
                "<KeyRelease>", 
                lambda e, qid=quest.id, w=desc_entry: self._update_quest_prop(qid, 'description', w.get())
            )
            
            # Delete button
            ctk.CTkButton(
                item_frame, text="✕", width=28, height=28, 
                fg_color="transparent", hover_color=COLOR_ERROR,
                command=lambda qid=quest.id: self._delete_quest(qid)
            ).grid(row=0, rowspan=3, column=2, padx=5, pady=5)

    def _add_quest(self):
        """Adds a new quest."""
        self.app._save_state_for_undo("Add Quest")
        new_quest_id = f"new_quest_{len(self.app.quests)}"
        
        # Ensure unique ID
        while new_quest_id in self.app.quests:
            new_quest_id += "_"
        
        self.app.quests[new_quest_id] = Quest(quest_id=new_quest_id)
        self.update_panel()

    def _rename_quest(self, old_id, new_id):
        """Renames a quest."""
        if not new_id or (new_id in self.app.quests and new_id != old_id):
            return
        
        self.app._save_state_for_undo("Rename Quest")
        quest = self.app.quests.pop(old_id)
        quest.id = new_id
        self.app.quests[new_id] = quest

    def _update_quest_prop(self, quest_id, prop, value):
        """Updates a quest property."""
        if quest_id in self.app.quests:
            self.app._save_state_for_undo("Update Quest Property")
            setattr(self.app.quests[quest_id], prop, value)

    def _delete_quest(self, quest_id):
        """Deletes a quest."""
        if messagebox.askyesno("Delete Quest", f"Delete quest '{quest_id}'?"):
            self.app._save_state_for_undo("Delete Quest")
            self.app.quests.pop(quest_id, None)
            self.update_panel()