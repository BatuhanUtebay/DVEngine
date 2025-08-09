# dvge/ui/project_panel.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from ..theme import *
from ..data_models import Quest

class ProjectPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.create_global_tabs()

    def create_global_tabs(self):
        # --- Player Tab ---
        player_frame = ctk.CTkFrame(self, fg_color="transparent")
        player_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        player_frame.grid_columnconfigure(0, weight=1)
        player_frame.grid_rowconfigure(1, weight=1)
        player_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(player_frame, text="Player Stats", font=FONT_SUBTITLE).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.player_stats_frame = ctk.CTkScrollableFrame(player_frame, fg_color="transparent")
        self.player_stats_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.player_stats_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(player_frame, text="+ Add Stat", command=self.add_player_stat).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(player_frame, text="Starting Inventory", font=FONT_SUBTITLE).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.player_inventory_frame = ctk.CTkScrollableFrame(player_frame, fg_color="transparent")
        self.player_inventory_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        self.player_inventory_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(player_frame, text="+ Add Item", command=self.add_inventory_item).grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # --- Flags Tab ---
        flags_frame = ctk.CTkFrame(self, fg_color="transparent")
        flags_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        flags_frame.grid_columnconfigure(0, weight=1)
        flags_frame.grid_rowconfigure(0, weight=1)
        self.flags_frame = ctk.CTkScrollableFrame(flags_frame, label_text="Story Flags", label_font=FONT_SUBTITLE)
        self.flags_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.flags_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(flags_frame, text="+ Add Flag", command=self.add_story_flag).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Quests Tab ---
        quests_frame = ctk.CTkFrame(self, fg_color="transparent")
        quests_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        quests_frame.grid_columnconfigure(0, weight=1)
        quests_frame.grid_rowconfigure(0, weight=1)
        self.quests_frame = ctk.CTkScrollableFrame(quests_frame, label_text="Quests / Journal", label_font=FONT_SUBTITLE)
        self.quests_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.quests_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(quests_frame, text="+ Add Quest", command=self.add_quest).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Project Settings Tab ---
        project_settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        project_settings_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        project_settings_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(project_settings_frame, text="Main Font:", font=FONT_BODY_BOLD).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.app.prop_widgets["font_combo"] = ctk.CTkComboBox(project_settings_frame, values=["Merriweather", "Lato", "Roboto", "Playfair Display", "Source Code Pro"], font=FONT_BODY)
        self.app.prop_widgets["font_combo"].grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(project_settings_frame, text="Title Font:", font=FONT_BODY_BOLD).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.app.prop_widgets["title_font_combo"] = ctk.CTkComboBox(project_settings_frame, values=["Special Elite", "Cinzel", "Orbitron", "Press Start 2P"], font=FONT_BODY)
        self.app.prop_widgets["title_font_combo"].grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(project_settings_frame, text="Background:", font=FONT_BODY_BOLD).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.app.prop_widgets["background_entry"] = ctk.CTkEntry(project_settings_frame, font=FONT_BODY, placeholder_text="#263238 or url(...)")
        self.app.prop_widgets["background_entry"].grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkButton(project_settings_frame, text="Save Project Settings", command=self.save_project_settings).grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    def update_all_panels(self):
        self.update_player_panel()
        self.update_flags_panel()
        self.update_quests_panel()
        self.update_project_settings_panel()

    def update_player_panel(self):
        for w in self.player_stats_frame.winfo_children(): w.destroy()
        for stat, value in self.app.player_stats.items():
            frame = ctk.CTkFrame(self.player_stats_frame, fg_color=COLOR_SECONDARY_FRAME)
            frame.pack(fill="x", pady=2)
            name_entry = ctk.CTkEntry(frame)
            name_entry.insert(0, stat)
            name_entry.pack(side="left", padx=5, expand=True, fill="x")
            name_entry.bind("<KeyRelease>", lambda e, old_name=stat, w=name_entry: self.rename_player_stat(old_name, w.get()))
            val_entry = ctk.CTkEntry(frame, width=80)
            val_entry.insert(0, str(value))
            val_entry.pack(side="left", padx=5)
            val_entry.bind("<KeyRelease>", lambda e, name=stat, w=val_entry: self.change_stat_default(name, w.get()))
            ctk.CTkButton(frame, text="✕", width=28, height=28, fg_color="transparent", hover_color=COLOR_ERROR, command=lambda s=stat: self.delete_player_stat(s)).pack(side="right", padx=5)

        for w in self.player_inventory_frame.winfo_children(): w.destroy()
        for i, item in enumerate(self.app.player_inventory):
            frame = ctk.CTkFrame(self.player_inventory_frame, fg_color=COLOR_SECONDARY_FRAME)
            frame.pack(fill="x", pady=2)
            frame.grid_columnconfigure(0, weight=1)
            name_entry = ctk.CTkEntry(frame, placeholder_text="Item Name")
            name_entry.insert(0, item.get("name", ""))
            name_entry.grid(row=0, column=0, padx=5, pady=(5,2), sticky="ew")
            name_entry.bind("<KeyRelease>", lambda e, idx=i, w=name_entry: self.update_inventory_item(idx, 'name', w.get()))
            desc_entry = ctk.CTkEntry(frame, placeholder_text="Item Description")
            desc_entry.insert(0, item.get("description", ""))
            desc_entry.grid(row=1, column=0, padx=5, pady=(2,5), sticky="ew")
            desc_entry.bind("<KeyRelease>", lambda e, idx=i, w=desc_entry: self.update_inventory_item(idx, 'description', w.get()))
            ctk.CTkButton(frame, text="✕", width=28, height=28, fg_color="transparent", hover_color=COLOR_ERROR, command=lambda idx=i: self.delete_inventory_item(idx)).grid(row=0, rowspan=2, column=1, padx=5)

    def add_player_stat(self):
        self.app._save_state_for_undo("Add Stat")
        new_stat_name = f"new_stat_{len(self.app.player_stats)}"
        self.app.player_stats[new_stat_name] = 10
        self.update_player_panel()
        self.app.sidebar.update_properties_panel()

    def rename_player_stat(self, old_name, new_name):
        if not new_name or (new_name in self.app.player_stats and new_name != old_name): return
        self.app._save_state_for_undo("Rename Stat")
        self.app.player_stats[new_name] = self.app.player_stats.pop(old_name)
        self.app.sidebar.update_properties_panel()

    def change_stat_default(self, name, value_str):
        try: value = int(value_str)
        except (ValueError, KeyError): return
        if self.app.player_stats[name] != value:
            self.app._save_state_for_undo("Change Stat Default")
            self.app.player_stats[name] = value

    def delete_player_stat(self, stat_name):
        if messagebox.askyesno("Delete Stat", f"Delete '{stat_name}'? This cannot be undone easily."):
            self.app._save_state_for_undo("Delete Stat")
            self.app.player_stats.pop(stat_name, None)
            self.update_player_panel()
            self.app.sidebar.update_properties_panel()

    def add_inventory_item(self):
        self.app._save_state_for_undo("Add Item")
        self.app.player_inventory.append({"name": f"new_item_{len(self.app.player_inventory)}", "description": "A new item."})
        self.update_player_panel()
        self.app.sidebar.update_properties_panel()
        
    def update_inventory_item(self, index, key, value):
        if index < len(self.app.player_inventory):
            self.app._save_state_for_undo("Update Item")
            self.app.player_inventory[index][key] = value
            self.app.sidebar.update_properties_panel()

    def delete_inventory_item(self, index):
        if messagebox.askyesno("Delete Item", f"Delete '{self.app.player_inventory[index]['name']}'?"):
            self.app._save_state_for_undo("Delete Item")
            del self.app.player_inventory[index]
            self.update_player_panel()
            self.app.sidebar.update_properties_panel()

    def update_flags_panel(self):
        for w in self.flags_frame.winfo_children(): w.destroy()
        for flag, value in self.app.story_flags.items():
            frame = ctk.CTkFrame(self.flags_frame, fg_color=COLOR_SECONDARY_FRAME)
            frame.pack(fill="x", pady=2)
            name_entry = ctk.CTkEntry(frame)
            name_entry.insert(0, flag)
            name_entry.pack(side="left", padx=5, expand=True, fill="x")
            name_entry.bind("<KeyRelease>", lambda e, old_name=flag, w=name_entry: self.rename_story_flag(old_name, w.get()))
            val_combo = ctk.CTkComboBox(frame, values=["true", "false"], width=90)
            val_combo.set("true" if value else "false")
            val_combo.configure(command=lambda c, f=flag: self.change_flag_default(f, c))
            val_combo.pack(side="left", padx=5)
            ctk.CTkButton(frame, text="✕", width=28, height=28, fg_color="transparent", hover_color=COLOR_ERROR, command=lambda f=flag: self.delete_story_flag(f)).pack(side="right", padx=5)

    def add_story_flag(self):
        self.app._save_state_for_undo("Add Flag")
        self.app.story_flags[f"new_flag_{len(self.app.story_flags)}"] = False
        self.update_flags_panel()
        self.app.sidebar.update_properties_panel()
        
    def rename_story_flag(self, old_name, new_name):
        if not new_name or (new_name in self.app.story_flags and new_name != old_name): return
        self.app._save_state_for_undo("Rename Flag")
        self.app.story_flags[new_name] = self.app.story_flags.pop(old_name)
        self.app.sidebar.update_properties_panel()
        
    def change_flag_default(self, flag_name, value_str):
        self.app._save_state_for_undo("Change Flag Default")
        self.app.story_flags[flag_name] = (value_str == "true")
        
    def delete_story_flag(self, flag_name):
        if messagebox.askyesno("Delete Flag", f"Delete '{flag_name}'?"):
            self.app._save_state_for_undo("Delete Flag")
            self.app.story_flags.pop(flag_name, None)
            self.update_flags_panel()
            self.app.sidebar.update_properties_panel()

    def update_quests_panel(self):
        for w in self.quests_frame.winfo_children(): w.destroy()
        for quest_id, quest in self.app.quests.items():
            frame = ctk.CTkFrame(self.quests_frame, fg_color=COLOR_SECONDARY_FRAME)
            frame.pack(fill="x", pady=4, padx=2)
            frame.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(frame, text="ID:", font=FONT_BODY).grid(row=0, column=0, padx=5, pady=2, sticky="w")
            id_entry = ctk.CTkEntry(frame, font=FONT_BODY)
            id_entry.insert(0, quest.id)
            id_entry.grid(row=0, column=1, sticky="ew", padx=5)
            id_entry.bind("<KeyRelease>", lambda e, old_id=quest_id, w=id_entry: self.rename_quest(old_id, w.get()))
            ctk.CTkLabel(frame, text="Name:", font=FONT_BODY).grid(row=1, column=0, padx=5, pady=2, sticky="w")
            name_entry = ctk.CTkEntry(frame, font=FONT_BODY)
            name_entry.insert(0, quest.name)
            name_entry.grid(row=1, column=1, sticky="ew", padx=5)
            name_entry.bind("<KeyRelease>", lambda e, qid=quest.id, w=name_entry: self.update_quest_prop(qid, 'name', w.get()))
            ctk.CTkLabel(frame, text="Desc:", font=FONT_BODY).grid(row=2, column=0, padx=5, pady=2, sticky="w")
            desc_entry = ctk.CTkEntry(frame, font=FONT_BODY)
            desc_entry.insert(0, quest.description)
            desc_entry.grid(row=2, column=1, sticky="ew", padx=5)
            desc_entry.bind("<KeyRelease>", lambda e, qid=quest.id, w=desc_entry: self.update_quest_prop(qid, 'description', w.get()))
            ctk.CTkButton(frame, text="✕", width=28, height=28, fg_color="transparent", hover_color=COLOR_ERROR, command=lambda qid=quest.id: self.delete_quest(qid)).grid(row=0, rowspan=3, column=2, padx=5)

    def add_quest(self):
        self.app._save_state_for_undo("Add Quest")
        new_quest_id = f"new_quest_{len(self.app.quests)}"
        while new_quest_id in self.app.quests: new_quest_id += "_"
        self.app.quests[new_quest_id] = Quest(quest_id=new_quest_id)
        self.update_quests_panel()
        self.app.sidebar.update_properties_panel()

    def rename_quest(self, old_id, new_id):
        if not new_id or (new_id in self.app.quests and new_id != old_id): return
        self.app._save_state_for_undo("Rename Quest")
        quest = self.app.quests.pop(old_id)
        quest.id = new_id
        self.app.quests[new_id] = quest
        self.app.sidebar.update_properties_panel()

    def update_quest_prop(self, quest_id, prop, value):
        if quest_id in self.app.quests:
            self.app._save_state_for_undo("Update Quest Property")
            setattr(self.app.quests[quest_id], prop, value)

    def delete_quest(self, quest_id):
        if messagebox.askyesno("Delete Quest", f"Delete quest '{quest_id}'?"):
            self.app._save_state_for_undo("Delete Quest")
            self.app.quests.pop(quest_id, None)
            self.update_quests_panel()
            self.app.sidebar.update_properties_panel()
            
    def update_project_settings_panel(self):
        self.app.prop_widgets["font_combo"].set(self.app.project_settings.get("font", "Merriweather"))
        self.app.prop_widgets["title_font_combo"].set(self.app.project_settings.get("title_font", "Special Elite"))
        self.app.prop_widgets["background_entry"].delete(0, 'end')
        self.app.prop_widgets["background_entry"].insert(0, self.app.project_settings.get("background", ""))

    def save_project_settings(self):
        self.app._save_state_for_undo("Save Project Settings")
        self.app.project_settings["font"] = self.app.prop_widgets["font_combo"].get()
        self.app.project_settings["title_font"] = self.app.prop_widgets["title_font_combo"].get()
        self.app.project_settings["background"] = self.app.prop_widgets["background_entry"].get()
        messagebox.showinfo("Saved", "Project settings have been saved.")
