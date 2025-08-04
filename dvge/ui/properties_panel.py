# dvge/ui/properties_panel.py
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import customtkinter as ctk
from ..constants import *

class PropertiesPanel(ctk.CTkTabview):
    def __init__(self, parent, app):
        super().__init__(parent, width=450)
        self.app = app
        
        for tab_name in ["Node", "Choices", "Player", "Flags", "Project"]: self.add(tab_name)
        
        self.prop_widgets = {}
        self.create_properties_widgets()

    def create_properties_widgets(self):
        """Creates all the widgets for the right-hand properties panel."""
        # --- Node Tab ---
        node_tab = self.tab("Node")
        node_tab.grid_columnconfigure(0, weight=1)
        
        info_frame = ctk.CTkFrame(node_tab, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text="Node ID:", font=FONT_PROPERTIES_LABEL).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.prop_widgets["id_var"] = tk.StringVar()
        self.prop_widgets["id_entry"] = ctk.CTkEntry(info_frame, textvariable=self.prop_widgets["id_var"], font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["id_entry"].grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(info_frame, text="NPC/Narrator:", font=FONT_PROPERTIES_LABEL).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.prop_widgets["npc_entry"] = ctk.CTkEntry(info_frame, font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["npc_entry"].grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(info_frame, text="Theme:", font=FONT_PROPERTIES_LABEL).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.prop_widgets["theme_combo"] = ctk.CTkComboBox(info_frame, values=["theme-default", "theme-dream", "theme-ritual", "theme-revelation", "theme-escape"], font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["theme_combo"].grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(info_frame, text="Chapter Title:", font=FONT_PROPERTIES_LABEL).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.prop_widgets["chapter_entry"] = ctk.CTkEntry(info_frame, font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["chapter_entry"].grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(info_frame, text="Set Node Color", command=self.set_node_color).grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Background Image Section
        bg_frame = ctk.CTkFrame(node_tab, fg_color="transparent")
        bg_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))
        bg_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(bg_frame, text="Background Image:", font=FONT_PROPERTIES_LABEL).pack(side="top", anchor="w", padx=5)
        
        bg_entry_frame = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_entry_frame.pack(fill="x", padx=5)
        bg_entry_frame.grid_columnconfigure(0, weight=1)
        self.prop_widgets["bg_image_entry"] = ctk.CTkEntry(bg_entry_frame, font=FONT_PROPERTIES_ENTRY, placeholder_text="No image selected...")
        self.prop_widgets["bg_image_entry"].grid(row=0, column=0, sticky="ew", padx=(0,5))
        ctk.CTkButton(bg_entry_frame, text="Browse...", width=80, command=self.select_background_image).grid(row=0, column=1)
        
        # Audio File Section
        audio_frame = ctk.CTkFrame(node_tab, fg_color="transparent")
        audio_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,5))
        audio_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(audio_frame, text="Audio (MP3):", font=FONT_PROPERTIES_LABEL).pack(side="top", anchor="w", padx=5)
        
        audio_entry_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        audio_entry_frame.pack(fill="x", padx=5)
        audio_entry_frame.grid_columnconfigure(0, weight=1)
        self.prop_widgets["audio_entry"] = ctk.CTkEntry(audio_entry_frame, font=FONT_PROPERTIES_ENTRY, placeholder_text="No audio selected...")
        self.prop_widgets["audio_entry"].grid(row=0, column=0, sticky="ew", padx=(0,5))
        ctk.CTkButton(audio_entry_frame, text="Browse...", width=80, command=self.select_audio_file).grid(row=0, column=1)


        dialogue_frame = ctk.CTkFrame(node_tab, fg_color="transparent")
        dialogue_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        node_tab.grid_rowconfigure(3, weight=1)
        dialogue_frame.grid_columnconfigure(0, weight=1)
        dialogue_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(dialogue_frame, text="Dialogue/Text:", font=FONT_PROPERTIES_LABEL).grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.prop_widgets["text_box"] = ctk.CTkTextbox(dialogue_frame, wrap="word", font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["text_box"].grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0,5))
        
        ctk.CTkButton(node_tab, text="Save Node Changes", command=self.save_properties_to_node).grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        # --- Choices Tab ---
        choices_tab = self.tab("Choices")
        choices_tab.grid_rowconfigure(0, weight=1)
        choices_tab.grid_columnconfigure(0, weight=1)

        self.options_frame = ctk.CTkScrollableFrame(choices_tab)
        self.options_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.options_frame.grid_columnconfigure(0, weight=1)

        add_choice_button = ctk.CTkButton(choices_tab, text="+ Add Choice", command=self.add_choice_from_panel)
        add_choice_button.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.prop_widgets["add_choice_button"] = add_choice_button

        # --- Player Tab ---
        player_tab = self.tab("Player")
        player_tab.grid_columnconfigure(0, weight=1)
        player_tab.grid_rowconfigure(1, weight=1)
        player_tab.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(player_tab, text="Player Stats", font=FONT_PROPERTIES_LABEL).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.player_stats_frame = ctk.CTkScrollableFrame(player_tab)
        self.player_stats_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.player_stats_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(player_tab, text="+ Add Stat", command=self.add_player_stat).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(player_tab, text="Starting Inventory", font=FONT_PROPERTIES_LABEL).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.player_inventory_frame = ctk.CTkScrollableFrame(player_tab)
        self.player_inventory_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)
        self.player_inventory_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(player_tab, text="+ Add Item", command=self.add_inventory_item).grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # --- Flags Tab ---
        flags_tab = self.tab("Flags")
        flags_tab.grid_columnconfigure(0, weight=1)
        flags_tab.grid_rowconfigure(0, weight=1)
        self.flags_frame = ctk.CTkScrollableFrame(flags_tab, label_text="Story Flags")
        self.flags_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.flags_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(flags_tab, text="+ Add Flag", command=self.add_story_flag).grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Project Settings Tab ---
        project_tab = self.tab("Project")
        project_tab.grid_columnconfigure(0, weight=1)

        visuals_frame = ctk.CTkFrame(project_tab, fg_color="transparent")
        visuals_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        visuals_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(visuals_frame, text="Main Font:", font=FONT_PROPERTIES_LABEL).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.prop_widgets["font_combo"] = ctk.CTkComboBox(visuals_frame, values=["Merriweather", "Lato", "Roboto", "Playfair Display", "Source Code Pro"], font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["font_combo"].grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(visuals_frame, text="Title Font:", font=FONT_PROPERTIES_LABEL).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.prop_widgets["title_font_combo"] = ctk.CTkComboBox(visuals_frame, values=["Special Elite", "Cinzel", "Orbitron", "Press Start 2P"], font=FONT_PROPERTIES_ENTRY)
        self.prop_widgets["title_font_combo"].grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(visuals_frame, text="Background:", font=FONT_PROPERTIES_LABEL).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.prop_widgets["background_entry"] = ctk.CTkEntry(visuals_frame, font=FONT_PROPERTIES_ENTRY, placeholder_text="#263238 or url(...)")
        self.prop_widgets["background_entry"].grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkButton(project_tab, text="Save Project Settings", command=self.save_project_settings).grid(row=1, column=0, pady=10, padx=10, sticky="ew")

    def select_background_image(self):
        """Opens a file dialog to select a background image for the active node."""
        if not self.app.active_node_id: return
        filepath = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("PNG Files", "*.png")]
        )
        if filepath:
            self.prop_widgets["bg_image_entry"].delete(0, 'end')
            self.prop_widgets["bg_image_entry"].insert(0, filepath)

    def select_audio_file(self):
        """Opens a file dialog to select an audio file for the active node."""
        if not self.app.active_node_id: return
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("MP3 Files", "*.mp3")]
        )
        if filepath:
            self.prop_widgets["audio_entry"].delete(0, 'end')
            self.prop_widgets["audio_entry"].insert(0, filepath)

    def update_all_panels(self):
        """Updates all property panel tabs."""
        self.update_properties_panel()
        self.update_player_panel()
        self.update_flags_panel()
        self.update_project_settings_panel()

    def update_properties_panel(self):
        """Updates the entire properties panel based on the currently active node."""
        for widget in self.options_frame.winfo_children(): widget.destroy()
        is_node_active = self.app.active_node_id and self.app.active_node_id in self.app.nodes
        
        # Enable or disable widgets based on whether a node is selected
        for name, widget in self.prop_widgets.items():
            if hasattr(widget, 'configure'):
                if name.startswith("font_") or name.startswith("title_") or name.startswith("background_"):
                    widget.configure(state="normal")
                    continue
                widget.configure(state="normal" if is_node_active else "disabled")

        if is_node_active:
            node = self.app.nodes[self.app.active_node_id]
            self.prop_widgets["id_var"].set(node.id)
            if node.id == "intro": self.prop_widgets["id_entry"].configure(state="readonly")
            
            self.prop_widgets["npc_entry"].delete(0, 'end'); self.prop_widgets["npc_entry"].insert(0, node.npc)
            self.prop_widgets["theme_combo"].set(node.backgroundTheme or "theme-default")
            self.prop_widgets["chapter_entry"].delete(0, 'end'); self.prop_widgets["chapter_entry"].insert(0, node.chapter)
            self.prop_widgets["text_box"].delete("1.0", "end"); self.prop_widgets["text_box"].insert("1.0", node.text)
            self.prop_widgets["bg_image_entry"].delete(0, 'end'); self.prop_widgets["bg_image_entry"].insert(0, node.backgroundImage)
            self.prop_widgets["audio_entry"].delete(0, 'end'); self.prop_widgets["audio_entry"].insert(0, node.audio)
            
            for i, option in enumerate(node.options): self.create_option_widget(i, option)
        else:
            self.prop_widgets["id_var"].set("No node selected")
            self.prop_widgets["id_entry"].configure(state="readonly")
            self.prop_widgets["npc_entry"].delete(0, 'end')
            self.prop_widgets["theme_combo"].set('')
            self.prop_widgets["chapter_entry"].delete(0, 'end')
            self.prop_widgets["bg_image_entry"].delete(0, 'end')
            self.prop_widgets["audio_entry"].delete(0, 'end')
            self.prop_widgets["text_box"].delete("1.0", "end")
            self.prop_widgets["text_box"].configure(state="disabled")

    def create_option_widget(self, index, option_data):
        """Creates the set of widgets for a single choice in the Choices tab."""
        option_frame = ctk.CTkFrame(self.options_frame, border_width=1, border_color="#555")
        option_frame.pack(fill="x", pady=5, padx=5)
        option_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(option_frame, text=f"Choice #{index+1}", font=(FONT_FAMILY, 11, "bold"), text_color="#3498DB").grid(row=0, column=0, columnspan=4, padx=5, pady=(5,2), sticky="w")
        
        ctk.CTkLabel(option_frame, text="Text:", font=FONT_PROPERTIES_ENTRY).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        text_entry = ctk.CTkEntry(option_frame, font=FONT_PROPERTIES_ENTRY)
        text_entry.insert(0, option_data.get("text", ""))
        text_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5)
        text_entry.bind("<KeyRelease>", lambda e, i=index, w=text_entry: self.on_option_prop_change(i, 'text', w.get()))

        node_ids = ["", "[End Game]"] + sorted(list(self.app.nodes.keys()))
        
        ctk.CTkLabel(option_frame, text="Next Node:", font=FONT_PROPERTIES_ENTRY).grid(row=2, column=0, padx=5, pady=2, sticky="w")
        combobox = ctk.CTkComboBox(option_frame, values=node_ids, font=FONT_PROPERTIES_ENTRY)
        combobox.set(option_data.get("nextNode", ""))
        combobox.configure(command=lambda choice, i=index: self.on_option_prop_change(i, 'nextNode', choice))
        combobox.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5)

        # --- Conditions ---
        cond_label = ctk.CTkLabel(option_frame, text="Conditions", font=(FONT_FAMILY, 10, "bold"))
        cond_label.grid(row=3, column=0, columnspan=4, sticky="w", padx=5, pady=(8,2))
        
        conditions_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        conditions_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5)
        
        if "conditions" not in option_data: option_data["conditions"] = []
        for cond_idx, cond in enumerate(option_data["conditions"]):
            self.create_condition_row(conditions_frame, index, cond_idx, cond)
        
        ctk.CTkButton(conditions_frame, text="+ Add Condition", height=20, command=lambda oi=index: self.add_condition(oi)).pack(fill="x", pady=2)

        # --- Effects ---
        eff_label = ctk.CTkLabel(option_frame, text="Effects", font=(FONT_FAMILY, 10, "bold"))
        eff_label.grid(row=5, column=0, columnspan=4, sticky="w", padx=5, pady=(8,2))

        effects_frame = ctk.CTkFrame(option_frame, fg_color="transparent")
        effects_frame.grid(row=6, column=0, columnspan=4, sticky="ew", padx=5)

        if "effects" not in option_data: option_data["effects"] = []
        for effect_idx, effect in enumerate(option_data["effects"]):
            self.create_effect_row(effects_frame, index, effect_idx, effect)
        
        ctk.CTkButton(effects_frame, text="+ Add Effect", height=20, command=lambda oi=index: self.add_effect(oi)).pack(fill="x", pady=2)
        
        ctk.CTkButton(option_frame, text="Remove Choice", fg_color="#C0392B", hover_color="#A93226", height=20, command=lambda i=index: self.remove_option_from_node(i)).grid(row=7, column=0, columnspan=4, pady=8, padx=5)

    def create_condition_row(self, parent, opt_idx, cond_idx, cond_data):
        """Creates a single row of widgets for a condition."""
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", pady=2)
        
        cond_type = cond_data.get("type", "stat")
        
        def on_type_change(choice):
            cond_data["type"] = choice.lower()
            # Rebuild this row
            self.update_properties_panel()
        
        type_combo = ctk.CTkComboBox(row_frame, values=["Stat", "Item", "Flag"], width=80, command=on_type_change)
        type_combo.set(cond_type.capitalize())
        type_combo.pack(side="left", padx=2)

        if cond_type == "stat":
            stat_combo = ctk.CTkComboBox(row_frame, values=list(self.app.player_stats.keys()), width=100, command=lambda c: self.on_condition_prop_change(opt_idx, cond_idx, 'subject', c))
            stat_combo.set(cond_data.get("subject", ""))
            stat_combo.pack(side="left", padx=2)
            
            op_combo = ctk.CTkComboBox(row_frame, values=["==", "!=", ">", "<", ">=", "<="], width=60, command=lambda c: self.on_condition_prop_change(opt_idx, cond_idx, 'operator', c))
            op_combo.set(cond_data.get("operator", "=="))
            op_combo.pack(side="left", padx=2)
            
            val_entry = ctk.CTkEntry(row_frame, width=80)
            val_entry.insert(0, str(cond_data.get("value", "")))
            val_entry.bind("<KeyRelease>", lambda e, w=val_entry: self.on_condition_prop_change(opt_idx, cond_idx, 'value', w.get()))
            val_entry.pack(side="left", padx=2)
        
        elif cond_type == "item":
            op_combo = ctk.CTkComboBox(row_frame, values=["has", "does not have"], width=120, command=lambda c: self.on_condition_prop_change(opt_idx, cond_idx, 'operator', c))
            op_combo.set(cond_data.get("operator", "has"))
            op_combo.pack(side="left", padx=2)
            
            item_entry = ctk.CTkEntry(row_frame)
            item_entry.insert(0, cond_data.get("subject", ""))
            item_entry.bind("<KeyRelease>", lambda e, w=item_entry: self.on_condition_prop_change(opt_idx, cond_idx, 'subject', w.get()))
            item_entry.pack(side="left", padx=2, expand=True, fill="x")

        elif cond_type == "flag":
            flag_combo = ctk.CTkComboBox(row_frame, values=list(self.app.story_flags.keys()), width=120, command=lambda c: self.on_condition_prop_change(opt_idx, cond_idx, 'subject', c))
            flag_combo.set(cond_data.get("subject", ""))
            flag_combo.pack(side="left", padx=2)
            
            op_combo = ctk.CTkComboBox(row_frame, values=["is", "is not"], width=80, command=lambda c: self.on_condition_prop_change(opt_idx, cond_idx, 'operator', c))
            op_combo.set(cond_data.get("operator", "is"))
            op_combo.pack(side="left", padx=2)

            val_combo = ctk.CTkComboBox(row_frame, values=["true", "false"], width=80, command=lambda c: self.on_condition_prop_change(opt_idx, cond_idx, 'value', c == "true"))
            val_combo.set("true" if cond_data.get("value", True) else "false")
            val_combo.pack(side="left", padx=2)

        remove_btn = ctk.CTkButton(row_frame, text="X", width=25, fg_color="#C0392B", hover_color="#A93226", command=lambda oi=opt_idx, ci=cond_idx: self.remove_condition(oi, ci))
        remove_btn.pack(side="right", padx=2)

    def create_effect_row(self, parent, opt_idx, effect_idx, effect_data):
        """Creates a single row of widgets for an effect."""
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", pady=2)
        
        effect_type = effect_data.get("type", "stat")
        
        def on_type_change(choice):
            effect_data["type"] = choice.lower()
            self.update_properties_panel()
        
        type_combo = ctk.CTkComboBox(row_frame, values=["Stat", "Item", "Flag"], width=80, command=on_type_change)
        type_combo.set(effect_type.capitalize())
        type_combo.pack(side="left", padx=2)

        if effect_type == "stat":
            stat_combo = ctk.CTkComboBox(row_frame, values=list(self.app.player_stats.keys()), width=100, command=lambda c: self.on_effect_prop_change(opt_idx, effect_idx, 'subject', c))
            stat_combo.set(effect_data.get("subject", ""))
            stat_combo.pack(side="left", padx=2)
            
            op_combo = ctk.CTkComboBox(row_frame, values=["=", "+=", "-="], width=60, command=lambda c: self.on_effect_prop_change(opt_idx, effect_idx, 'operator', c))
            op_combo.set(effect_data.get("operator", "="))
            op_combo.pack(side="left", padx=2)
            
            val_entry = ctk.CTkEntry(row_frame, width=80)
            val_entry.insert(0, str(effect_data.get("value", "")))
            val_entry.bind("<KeyRelease>", lambda e, w=val_entry: self.on_effect_prop_change(opt_idx, effect_idx, 'value', w.get()))
            val_entry.pack(side="left", padx=2)
        
        elif effect_type == "item":
            op_combo = ctk.CTkComboBox(row_frame, values=["add", "remove"], width=100, command=lambda c: self.on_effect_prop_change(opt_idx, effect_idx, 'operator', c))
            op_combo.set(effect_data.get("operator", "add"))
            op_combo.pack(side="left", padx=2)
            
            item_entry = ctk.CTkEntry(row_frame)
            item_entry.insert(0, effect_data.get("subject", ""))
            item_entry.bind("<KeyRelease>", lambda e, w=item_entry: self.on_effect_prop_change(opt_idx, effect_idx, 'subject', w.get()))
            item_entry.pack(side="left", padx=2, expand=True, fill="x")

        elif effect_type == "flag":
            flag_combo = ctk.CTkComboBox(row_frame, values=list(self.app.story_flags.keys()), width=120, command=lambda c: self.on_effect_prop_change(opt_idx, effect_idx, 'subject', c))
            flag_combo.set(effect_data.get("subject", ""))
            flag_combo.pack(side="left", padx=2)
            
            ctk.CTkLabel(row_frame, text="to").pack(side="left", padx=2)

            val_combo = ctk.CTkComboBox(row_frame, values=["true", "false"], width=80, command=lambda c: self.on_effect_prop_change(opt_idx, effect_idx, 'value', c == "true"))
            val_combo.set("true" if effect_data.get("value", True) else "false")
            val_combo.pack(side="left", padx=2)

        remove_btn = ctk.CTkButton(row_frame, text="X", width=25, fg_color="#C0392B", hover_color="#A93226", command=lambda oi=opt_idx, ei=effect_idx: self.remove_effect(oi, ei))
        remove_btn.pack(side="right", padx=2)

    def on_option_prop_change(self, index, key, value):
        """Callback for when a property of a choice is changed in the UI."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if index < len(node.options):
            self.app._save_state_for_undo("Change Option Property")
            node.options[index][key] = value
            if key == 'text': self.app.canvas_manager.redraw_node(self.app.active_node_id)
            elif 'Node' in key: self.app.canvas_manager.draw_connections()

    def on_condition_prop_change(self, opt_idx, cond_idx, key, value):
        """Callback for when a property of a condition is changed."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options) and cond_idx < len(node.options[opt_idx]["conditions"]):
            self.app._save_state_for_undo("Change Condition")
            node.options[opt_idx]["conditions"][cond_idx][key] = value
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def on_effect_prop_change(self, opt_idx, effect_idx, key, value):
        """Callback for when a property of an effect is changed."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options) and effect_idx < len(node.options[opt_idx]["effects"]):
            self.app._save_state_for_undo("Change Effect")
            node.options[opt_idx]["effects"][effect_idx][key] = value
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def add_condition(self, opt_idx):
        """Adds a new default condition to a choice."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options):
            self.app._save_state_for_undo("Add Condition")
            node.options[opt_idx]["conditions"].append({'type': 'stat', 'subject': '', 'operator': '>=', 'value': 10})
            self.update_properties_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def remove_condition(self, opt_idx, cond_idx):
        """Removes a condition from a choice."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options) and cond_idx < len(node.options[opt_idx]["conditions"]):
            self.app._save_state_for_undo("Remove Condition")
            del node.options[opt_idx]["conditions"][cond_idx]
            self.update_properties_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def add_effect(self, opt_idx):
        """Adds a new default effect to a choice."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options):
            self.app._save_state_for_undo("Add Effect")
            node.options[opt_idx]["effects"].append({'type': 'stat', 'subject': '', 'operator': '+=', 'value': 1})
            self.update_properties_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def remove_effect(self, opt_idx, effect_idx):
        """Removes an effect from a choice."""
        if not self.app.active_node_id: return
        node = self.app.nodes[self.app.active_node_id]
        if opt_idx < len(node.options) and effect_idx < len(node.options[opt_idx]["effects"]):
            self.app._save_state_for_undo("Remove Effect")
            del node.options[opt_idx]["effects"][effect_idx]
            self.update_properties_panel()
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            
    def add_option_to_node(self, node_id):
        """Adds a new, empty option to a node's data."""
        if node_id and node_id in self.app.nodes:
            self.app._save_state_for_undo("Add Choice")
            self.app.nodes[node_id].options.append({"text": "New Option", "nextNode": ""})
            return True
        return False

    def add_choice_from_panel(self):
        """Callback for the '+ Add Choice' button in the properties panel."""
        if not self.app.active_node_id: return
        if self.add_option_to_node(self.app.active_node_id):
            self.app.canvas_manager.redraw_node(self.app.active_node_id)
            self.update_properties_panel()

    def remove_option_from_node(self, index):
        """Removes a choice from the active node."""
        if not self.app.active_node_id: return
        self.app._save_state_for_undo("Remove Choice")
        del self.app.nodes[self.app.active_node_id].options[index]
        self.app.canvas_manager.redraw_node(self.app.active_node_id)
        self.update_properties_panel()

    def set_node_color(self):
        """Opens a color chooser and sets the active node's color."""
        if not self.app.active_node_id: return
        color_code = colorchooser.askcolor(title="Choose node color")
        if color_code and color_code[1]:
            self.app._save_state_for_undo("Set Node Color")
            self.app.nodes[self.app.active_node_id].color = color_code[1]
            self.app.canvas_manager.redraw_node(self.app.active_node_id)

    def update_player_panel(self):
        """Redraws the widgets in the Player tab."""
        for w in self.player_stats_frame.winfo_children(): w.destroy()
        for stat, value in self.app.player_stats.items():
            frame = ctk.CTkFrame(self.player_stats_frame)
            frame.pack(fill="x", pady=2)
            name_entry = ctk.CTkEntry(frame)
            name_entry.insert(0, stat)
            name_entry.pack(side="left", padx=5, expand=True, fill="x")
            name_entry.bind("<KeyRelease>", lambda e, old_name=stat, w=name_entry: self.rename_player_stat(old_name, w.get()))
            
            val_entry = ctk.CTkEntry(frame, width=80)
            val_entry.insert(0, str(value))
            val_entry.pack(side="left", padx=5)
            val_entry.bind("<KeyRelease>", lambda e, name=stat, w=val_entry: self.change_stat_default(name, w.get()))

            ctk.CTkButton(frame, text="X", width=25, fg_color="#C0392B", hover_color="#A93226", command=lambda s=stat: self.delete_player_stat(s)).pack(side="right", padx=5)

        for w in self.player_inventory_frame.winfo_children(): w.destroy()
        for item in self.app.player_inventory:
            frame = ctk.CTkFrame(self.player_inventory_frame)
            frame.pack(fill="x", pady=2)
            name_entry = ctk.CTkEntry(frame)
            name_entry.insert(0, item)
            name_entry.pack(side="left", padx=5, expand=True, fill="x")
            name_entry.bind("<KeyRelease>", lambda e, old_name=item, w=name_entry: self.rename_inventory_item(old_name, w.get()))
            ctk.CTkButton(frame, text="X", width=25, fg_color="#C0392B", hover_color="#A93226", command=lambda i=item: self.delete_inventory_item(i)).pack(side="right", padx=5)

    def add_player_stat(self):
        self.app._save_state_for_undo("Add Stat")
        new_stat_name = f"new_stat_{len(self.app.player_stats)}"
        self.app.player_stats[new_stat_name] = 10
        self.update_player_panel()
        self.update_properties_panel()

    def rename_player_stat(self, old_name, new_name):
        if not new_name or (new_name in self.app.player_stats and new_name != old_name): return
        self.app._save_state_for_undo("Rename Stat")
        self.app.player_stats[new_name] = self.app.player_stats.pop(old_name)
        # Update references in choices (optional, but good practice)
        self.update_properties_panel()

    def change_stat_default(self, name, value_str):
        try:
            value = int(value_str)
            if self.app.player_stats[name] != value:
                self.app._save_state_for_undo("Change Stat Default")
                self.app.player_stats[name] = value
        except (ValueError, KeyError):
            pass

    def delete_player_stat(self, stat_name):
        if messagebox.askyesno("Delete Stat", f"Delete '{stat_name}'? This cannot be undone easily."):
            self.app._save_state_for_undo("Delete Stat")
            self.app.player_stats.pop(stat_name, None)
            self.update_player_panel()
            self.update_properties_panel()

    def add_inventory_item(self):
        self.app._save_state_for_undo("Add Item")
        self.app.player_inventory.append(f"new_item_{len(self.app.player_inventory)}")
        self.update_player_panel()
        self.update_properties_panel()
        
    def rename_inventory_item(self, old_name, new_name):
        if not new_name or (new_name in self.app.player_inventory and new_name != old_name): return
        self.app._save_state_for_undo("Rename Item")
        idx = self.app.player_inventory.index(old_name)
        self.app.player_inventory[idx] = new_name
        self.update_properties_panel()

    def delete_inventory_item(self, item_name):
        if messagebox.askyesno("Delete Item", f"Delete '{item_name}'?"):
            self.app._save_state_for_undo("Delete Item")
            self.app.player_inventory.remove(item_name)
            self.update_player_panel()
            self.update_properties_panel()

    def update_flags_panel(self):
        """Redraws the widgets in the Flags tab."""
        for w in self.flags_frame.winfo_children(): w.destroy()
        for flag, value in self.app.story_flags.items():
            frame = ctk.CTkFrame(self.flags_frame)
            frame.pack(fill="x", pady=2)
            
            name_entry = ctk.CTkEntry(frame)
            name_entry.insert(0, flag)
            name_entry.pack(side="left", padx=5, expand=True, fill="x")
            name_entry.bind("<KeyRelease>", lambda e, old_name=flag, w=name_entry: self.rename_story_flag(old_name, w.get()))
            
            val_combo = ctk.CTkComboBox(frame, values=["true", "false"], width=80)
            val_combo.set("true" if value else "false")
            val_combo.configure(command=lambda c, f=flag: self.change_flag_default(f, c))
            val_combo.pack(side="left", padx=5)

            ctk.CTkButton(frame, text="X", width=25, fg_color="#C0392B", hover_color="#A93226", command=lambda f=flag: self.delete_story_flag(f)).pack(side="right", padx=5)

    def add_story_flag(self):
        self.app._save_state_for_undo("Add Flag")
        self.app.story_flags[f"new_flag_{len(self.app.story_flags)}"] = False
        self.update_flags_panel()
        self.update_properties_panel()
        
    def rename_story_flag(self, old_name, new_name):
        if not new_name or (new_name in self.app.story_flags and new_name != old_name): return
        self.app._save_state_for_undo("Rename Flag")
        self.app.story_flags[new_name] = self.app.story_flags.pop(old_name)
        self.update_properties_panel()
        
    def change_flag_default(self, flag_name, value_str):
        self.app._save_state_for_undo("Change Flag Default")
        self.app.story_flags[flag_name] = (value_str == "true")
        
    def delete_story_flag(self, flag_name):
        if messagebox.askyesno("Delete Flag", f"Delete '{flag_name}'?"):
            self.app._save_state_for_undo("Delete Flag")
            self.app.story_flags.pop(flag_name, None)
            self.update_flags_panel()
            self.update_properties_panel()

    def save_properties_to_node(self):
        """Saves the data from the properties panel back to the active node object."""
        if not self.app.active_node_id: return
        self.app._save_state_for_undo("Save Node Properties")
        node = self.app.nodes[self.app.active_node_id]
        new_id = self.prop_widgets["id_var"].get()
        
        if new_id != node.id and new_id and node.id != "intro":
            if new_id in self.app.nodes:
                messagebox.showerror("Error", f"Node ID '{new_id}' already exists."); self.prop_widgets["id_var"].set(node.id); return
            if not new_id:
                messagebox.showerror("Error", "Node ID cannot be empty."); self.prop_widgets["id_var"].set(node.id); return
                
            old_id = node.id
            self.app.nodes[new_id] = self.app.nodes.pop(old_id); node.id = new_id
            for n in self.app.nodes.values():
                for opt in n.options:
                    if opt.get('nextNode') == old_id: opt['nextNode'] = new_id
            
            self.app.active_node_id = new_id
            self.app.selected_node_ids = [nid if nid != old_id else new_id for nid in self.app.selected_node_ids]
            
        node.npc = self.prop_widgets["npc_entry"].get()
        node.text = self.prop_widgets["text_box"].get("1.0", "end-1c")
        node.backgroundTheme = self.prop_widgets["theme_combo"].get()
        node.chapter = self.prop_widgets["chapter_entry"].get()
        node.backgroundImage = self.prop_widgets["bg_image_entry"].get()
        node.audio = self.prop_widgets["audio_entry"].get()
        
        self.app.canvas_manager.redraw_all_nodes()
        self.update_properties_panel()
        messagebox.showinfo("Saved", f"Changes for {self.app.active_node_id} have been saved.")

    def update_project_settings_panel(self):
        """Populates the Project tab with the current project settings."""
        self.prop_widgets["font_combo"].set(self.app.project_settings.get("font", "Merriweather"))
        self.prop_widgets["title_font_combo"].set(self.app.project_settings.get("title_font", "Special Elite"))
        self.prop_widgets["background_entry"].delete(0, 'end')
        self.prop_widgets["background_entry"].insert(0, self.app.project_settings.get("background", ""))

    def save_project_settings(self):
        """Saves the settings from the Project tab to the project_settings dictionary."""
        self.app._save_state_for_undo("Save Project Settings")
        self.app.project_settings["font"] = self.prop_widgets["font_combo"].get()
        self.app.project_settings["title_font"] = self.prop_widgets["title_font_combo"].get()
        self.app.project_settings["background"] = self.prop_widgets["background_entry"].get()
        messagebox.showinfo("Saved", "Project settings have been saved.")