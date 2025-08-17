# dvge/ui/windows/advanced_combat_editor.py

"""Advanced Combat Editor Window for detailed combat configuration."""

import tkinter as tk
import customtkinter as ctk
from ...constants import *
from ...models.advanced_combat_node import AdvancedCombatNode
import json


class AdvancedCombatEditor(ctk.CTkToplevel):
    """Dedicated editor window for advanced combat nodes."""
    
    def __init__(self, parent_app, node=None, position=None):
        super().__init__(parent_app)
        self.app = parent_app
        self.position = position  # Store the position for new nodes
        
        # Track if this is a new node or editing existing
        self.is_new_node = node is None
        
        # Create node with proper position if it's new
        if self.is_new_node:
            x, y = position if position else (100, 100)
            self.node = AdvancedCombatNode(x=x, y=y)
        else:
            self.node = node
            
        self.original_node_data = None
        
        # Store original data for cancel functionality
        if not self.is_new_node:
            self.original_node_data = self.node.to_dict()
        
        self.title("Advanced Combat Editor")
        self.geometry("1200x800")
        self.transient(parent_app)
        self.resizable(True, True)
        
        # Make window modal
        self.grab_set()
        
        self._setup_ui()
        self._load_node_data()
        
        # Center the window
        self.center_window()
        
    def center_window(self):
        """Center the window on the parent."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Sets up the combat editor UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_main_content()
        self._create_button_bar()
    
    def _create_header(self):
        """Creates the header with title and basic info."""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="⚔️ Advanced Combat Editor",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Node ID and basic info
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=15, pady=15, sticky="e")
        
        if not self.is_new_node:
            node_id_label = ctk.CTkLabel(info_frame, text=f"Node: {self.node.id}")
            node_id_label.pack(side="right", padx=(0, 10))
    
    def _create_main_content(self):
        """Creates the main tabbed content area."""
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Create tabs
        self.basic_tab = self.notebook.add("Basic Settings")
        self.enemies_tab = self.notebook.add("Enemies")
        self.allies_tab = self.notebook.add("Allies")
        self.environment_tab = self.notebook.add("Environment")
        self.rewards_tab = self.notebook.add("Rewards")
        self.advanced_tab = self.notebook.add("Advanced")
        
        self._setup_basic_tab()
        self._setup_enemies_tab()
        self._setup_allies_tab()
        self._setup_environment_tab()
        self._setup_rewards_tab()
        self._setup_advanced_tab()
    
    def _setup_basic_tab(self):
        """Sets up the basic settings tab."""
        # Make the tab scrollable
        self.basic_scroll = ctk.CTkScrollableFrame(self.basic_tab)
        self.basic_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Basic combat info
        basic_frame = ctk.CTkFrame(self.basic_scroll)
        basic_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(basic_frame, text="Combat Information", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # NPC Name
        npc_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        npc_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(npc_frame, text="NPC Name:", width=120).pack(side="left")
        self.npc_entry = ctk.CTkEntry(npc_frame, placeholder_text="Combat Encounter")
        self.npc_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Description text
        desc_frame = ctk.CTkFrame(basic_frame, fg_color="transparent")
        desc_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(desc_frame, text="Description:", width=120).pack(side="left", anchor="n")
        self.desc_text = ctk.CTkTextbox(desc_frame, height=80)
        self.desc_text.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Combat settings
        settings_frame = ctk.CTkFrame(self.basic_scroll)
        settings_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(settings_frame, text="Combat Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # Combat type
        type_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(type_frame, text="Combat Type:", width=120).pack(side="left")
        self.combat_type = ctk.CTkOptionMenu(type_frame, values=["advanced", "boss", "arena", "survival"])
        self.combat_type.pack(side="left", padx=(10, 0))
        
        # Initiative system
        init_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        init_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(init_frame, text="Initiative:", width=120).pack(side="left")
        self.initiative = ctk.CTkOptionMenu(init_frame, values=["agility", "random", "fixed"])
        self.initiative.pack(side="left", padx=(10, 0))
        
        # Escape settings
        escape_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        escape_frame.pack(fill="x", padx=15, pady=5)
        self.allow_escape = ctk.CTkCheckBox(escape_frame, text="Allow Escape")
        self.allow_escape.pack(side="left")
        
        ctk.CTkLabel(escape_frame, text="Difficulty:", width=80).pack(side="left", padx=(20, 5))
        self.escape_difficulty = ctk.CTkEntry(escape_frame, width=60, placeholder_text="10")
        self.escape_difficulty.pack(side="left")
        
        # Formation matters
        formation_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        formation_frame.pack(fill="x", padx=15, pady=5)
        self.formation_matters = ctk.CTkCheckBox(formation_frame, text="Formation Matters (Front/Back Row)")
        self.formation_matters.pack(side="left")
        
        # Turn limit
        turn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        turn_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(turn_frame, text="Turn Limit:", width=120).pack(side="left")
        self.turn_limit = ctk.CTkEntry(turn_frame, width=60, placeholder_text="0 (no limit)")
        self.turn_limit.pack(side="left", padx=(10, 0))
        
        # Node connections
        connections_frame = ctk.CTkFrame(self.basic_scroll)
        connections_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(connections_frame, text="Node Connections", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # Victory node
        victory_frame = ctk.CTkFrame(connections_frame, fg_color="transparent")
        victory_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(victory_frame, text="Victory Node:", width=120).pack(side="left")
        self.victory_node = ctk.CTkEntry(victory_frame, placeholder_text="Node ID for victory")
        self.victory_node.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Defeat node
        defeat_frame = ctk.CTkFrame(connections_frame, fg_color="transparent")
        defeat_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(defeat_frame, text="Defeat Node:", width=120).pack(side="left")
        self.defeat_node = ctk.CTkEntry(defeat_frame, placeholder_text="Node ID for defeat")
        self.defeat_node.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Escape node
        escape_node_frame = ctk.CTkFrame(connections_frame, fg_color="transparent")
        escape_node_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(escape_node_frame, text="Escape Node:", width=120).pack(side="left")
        self.escape_node = ctk.CTkEntry(escape_node_frame, placeholder_text="Node ID for escape")
        self.escape_node.pack(side="left", fill="x", expand=True, padx=(10, 0))
    
    def _setup_enemies_tab(self):
        """Sets up the enemies configuration tab."""
        enemies_main = ctk.CTkFrame(self.enemies_tab)
        enemies_main.pack(fill="both", expand=True, padx=10, pady=10)
        enemies_main.grid_columnconfigure(0, weight=1)
        enemies_main.grid_rowconfigure(1, weight=1)
        
        # Header with add button
        header = ctk.CTkFrame(enemies_main)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header, text="Enemies", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        add_enemy_btn = ctk.CTkButton(header, text="+ Add Enemy", command=self._add_enemy, width=100)
        add_enemy_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # Enemies list
        self.enemies_frame = ctk.CTkScrollableFrame(enemies_main)
        self.enemies_frame.grid(row=1, column=0, sticky="nsew")
    
    def _setup_allies_tab(self):
        """Sets up the allies configuration tab."""
        allies_main = ctk.CTkFrame(self.allies_tab)
        allies_main.pack(fill="both", expand=True, padx=10, pady=10)
        allies_main.grid_columnconfigure(0, weight=1)
        allies_main.grid_rowconfigure(1, weight=1)
        
        # Header with add button
        header = ctk.CTkFrame(allies_main)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header, text="Allies", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        add_ally_btn = ctk.CTkButton(header, text="+ Add Ally", command=self._add_ally, width=100)
        add_ally_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # Allies list
        self.allies_frame = ctk.CTkScrollableFrame(allies_main)
        self.allies_frame.grid(row=1, column=0, sticky="nsew")
    
    def _setup_environment_tab(self):
        """Sets up the environment and hazards tab."""
        env_scroll = ctk.CTkScrollableFrame(self.environment_tab)
        env_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Environment settings
        env_frame = ctk.CTkFrame(env_scroll)
        env_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(env_frame, text="Environment Settings", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # Environment type
        env_type_frame = ctk.CTkFrame(env_frame, fg_color="transparent")
        env_type_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(env_type_frame, text="Environment:", width=120).pack(side="left")
        self.environment = ctk.CTkOptionMenu(env_type_frame, values=["default", "dungeon", "forest", "desert", "tower", "underwater"])
        self.environment.pack(side="left", padx=(10, 0))
        
        # Weather
        weather_frame = ctk.CTkFrame(env_frame, fg_color="transparent")
        weather_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(weather_frame, text="Weather:", width=120).pack(side="left")
        self.weather = ctk.CTkOptionMenu(weather_frame, values=["clear", "rain", "storm", "sunny", "snow", "dark"])
        self.weather.pack(side="left", padx=(10, 0))
        
        # Environmental hazards
        hazards_frame = ctk.CTkFrame(env_scroll)
        hazards_frame.pack(fill="x")
        hazards_frame.grid_columnconfigure(0, weight=1)
        hazards_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        hazards_header = ctk.CTkFrame(hazards_frame)
        hazards_header.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        hazards_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(hazards_header, text="Environmental Hazards", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        add_hazard_btn = ctk.CTkButton(hazards_header, text="+ Add Hazard", command=self._add_hazard, width=100)
        add_hazard_btn.grid(row=0, column=1, padx=15, pady=10)
        
        # Hazards list
        self.hazards_frame = ctk.CTkScrollableFrame(hazards_frame, height=200)
        self.hazards_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    
    def _setup_rewards_tab(self):
        """Sets up the rewards and loot tab."""
        rewards_scroll = ctk.CTkScrollableFrame(self.rewards_tab)
        rewards_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        rewards_frame = ctk.CTkFrame(rewards_scroll)
        rewards_frame.pack(fill="x")
        
        ctk.CTkLabel(rewards_frame, text="Victory Rewards", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        # Experience reward
        exp_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        exp_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(exp_frame, text="Experience:", width=120).pack(side="left")
        self.experience_reward = ctk.CTkEntry(exp_frame, width=100, placeholder_text="100")
        self.experience_reward.pack(side="left", padx=(10, 0))
        
        # Gold reward
        gold_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        gold_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(gold_frame, text="Gold:", width=120).pack(side="left")
        self.gold_reward = ctk.CTkEntry(gold_frame, width=100, placeholder_text="50")
        self.gold_reward.pack(side="left", padx=(10, 0))
        
        # Skill points
        skill_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        skill_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(skill_frame, text="Skill Points:", width=120).pack(side="left")
        self.skill_points_reward = ctk.CTkEntry(skill_frame, width=100, placeholder_text="1")
        self.skill_points_reward.pack(side="left", padx=(10, 0))
        
        # Item rewards
        items_frame = ctk.CTkFrame(rewards_scroll)
        items_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(items_frame, text="Item Rewards", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.item_rewards_text = ctk.CTkTextbox(items_frame, height=120)
        self.item_rewards_text.pack(fill="x", padx=15, pady=(0, 15))
        self.item_rewards_text.insert("0.0", "Enter item rewards as JSON, e.g.:\n[\n  {\n    \"name\": \"Magic Sword\",\n    \"description\": \"A powerful weapon\"\n  }\n]")
    
    def _setup_advanced_tab(self):
        """Sets up the advanced settings tab."""
        advanced_scroll = ctk.CTkScrollableFrame(self.advanced_tab)
        advanced_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Victory conditions
        victory_frame = ctk.CTkFrame(advanced_scroll)
        victory_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(victory_frame, text="Victory Conditions", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.victory_conditions = ctk.CTkTextbox(victory_frame, height=80)
        self.victory_conditions.pack(fill="x", padx=15, pady=(0, 15))
        self.victory_conditions.insert("0.0", "[\"defeat_all_enemies\"]")
        
        # Defeat conditions
        defeat_frame = ctk.CTkFrame(advanced_scroll)
        defeat_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(defeat_frame, text="Defeat Conditions", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.defeat_conditions = ctk.CTkTextbox(defeat_frame, height=80)
        self.defeat_conditions.pack(fill="x", padx=15, pady=(0, 15))
        self.defeat_conditions.insert("0.0", "[\"party_defeated\"]")
        
        # Special rules
        rules_frame = ctk.CTkFrame(advanced_scroll)
        rules_frame.pack(fill="x")
        
        ctk.CTkLabel(rules_frame, text="Special Rules", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.special_rules = ctk.CTkTextbox(rules_frame, height=100)
        self.special_rules.pack(fill="x", padx=15, pady=(0, 15))
        self.special_rules.insert("0.0", "[]")
    
    def _create_button_bar(self):
        """Creates the bottom button bar."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel",
            command=self._cancel,
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.grid(row=0, column=0, padx=(15, 5), pady=15)
        
        # Save button
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Combat Node",
            command=self._save_node
        )
        save_btn.grid(row=0, column=2, padx=(5, 15), pady=15)
        
        # Preview button (if not new node)
        if not self.is_new_node:
            preview_btn = ctk.CTkButton(
                button_frame,
                text="Preview Combat",
                command=self._preview_combat,
                fg_color="orange",
                hover_color="darkorange"
            )
            preview_btn.grid(row=0, column=1, padx=5, pady=15)
    
    def _load_node_data(self):
        """Loads existing node data into the form."""
        if self.is_new_node:
            return
            
        # Basic settings
        self.npc_entry.insert(0, getattr(self.node, 'npc', ''))
        self.desc_text.insert("0.0", getattr(self.node, 'text', ''))
        
        self.combat_type.set(getattr(self.node, 'combat_type', 'advanced'))
        self.initiative.set(getattr(self.node, 'initiative_system', 'agility'))
        
        if getattr(self.node, 'allow_escape', True):
            self.allow_escape.select()
        self.escape_difficulty.insert(0, str(getattr(self.node, 'escape_difficulty', 10)))
        
        if getattr(self.node, 'formation_matters', True):
            self.formation_matters.select()
        self.turn_limit.insert(0, str(getattr(self.node, 'turn_limit', 0)))
        
        # Node connections
        self.victory_node.insert(0, getattr(self.node, 'victory_node', ''))
        self.defeat_node.insert(0, getattr(self.node, 'defeat_node', ''))
        self.escape_node.insert(0, getattr(self.node, 'escape_node', ''))
        
        # Environment
        self.environment.set(getattr(self.node, 'environment', 'default'))
        self.weather.set(getattr(self.node, 'weather', 'clear'))
        
        # Rewards
        self.experience_reward.insert(0, str(getattr(self.node, 'experience_reward', 100)))
        self.gold_reward.insert(0, str(getattr(self.node, 'gold_reward', 50)))
        self.skill_points_reward.insert(0, str(getattr(self.node, 'skill_points_reward', 1)))
        
        # Item rewards
        item_rewards = getattr(self.node, 'item_rewards', [])
        if item_rewards:
            self.item_rewards_text.delete("0.0", "end")
            self.item_rewards_text.insert("0.0", json.dumps(item_rewards, indent=2))
        
        # Advanced settings
        victory_conditions = getattr(self.node, 'victory_conditions', ["defeat_all_enemies"])
        self.victory_conditions.delete("0.0", "end")
        self.victory_conditions.insert("0.0", json.dumps(victory_conditions, indent=2))
        
        defeat_conditions = getattr(self.node, 'defeat_conditions', ["party_defeated"])
        self.defeat_conditions.delete("0.0", "end")
        self.defeat_conditions.insert("0.0", json.dumps(defeat_conditions, indent=2))
        
        special_rules = getattr(self.node, 'special_rules', [])
        self.special_rules.delete("0.0", "end")
        self.special_rules.insert("0.0", json.dumps(special_rules, indent=2))
        
        # Load enemies, allies, and hazards
        self._refresh_enemies_list()
        self._refresh_allies_list()
        self._refresh_hazards_list()
    
    def _refresh_enemies_list(self):
        """Refreshes the enemies list display."""
        # Clear existing widgets
        for widget in self.enemies_frame.winfo_children():
            widget.destroy()
        
        enemies = getattr(self.node, 'enemies', [])
        for i, enemy in enumerate(enemies):
            self._create_enemy_widget(enemy, i)
    
    def _create_enemy_widget(self, enemy, index):
        """Creates a widget for editing an enemy."""
        enemy_frame = ctk.CTkFrame(self.enemies_frame)
        enemy_frame.pack(fill="x", pady=5)
        enemy_frame.grid_columnconfigure(1, weight=1)
        
        # Enemy header
        header = ctk.CTkFrame(enemy_frame, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 5))
        header.grid_columnconfigure(1, weight=1)
        
        enemy_label = ctk.CTkLabel(header, text=f"🗡️ {enemy.get('name', 'Enemy')} (Level {enemy.get('level', 1)})", font=ctk.CTkFont(weight="bold"))
        enemy_label.grid(row=0, column=0, sticky="w")
        
        remove_btn = ctk.CTkButton(header, text="❌", width=30, command=lambda idx=index: self._remove_enemy(idx))
        remove_btn.grid(row=0, column=2)
        
        # Enemy details in a compact grid
        details_frame = ctk.CTkFrame(enemy_frame, fg_color="transparent")
        details_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
        details_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Row 1: Name, Level, AI Type
        ctk.CTkLabel(details_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        name_entry = ctk.CTkEntry(details_frame, width=100)
        name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        name_entry.insert(0, enemy.get('name', ''))
        name_entry.bind('<KeyRelease>', lambda e, idx=index, field='name': self._update_enemy_field(idx, field, name_entry.get()))
        
        ctk.CTkLabel(details_frame, text="Level:").grid(row=0, column=2, sticky="w", padx=(10, 5))
        level_entry = ctk.CTkEntry(details_frame, width=60)
        level_entry.grid(row=0, column=3, sticky="w", padx=5)
        level_entry.insert(0, str(enemy.get('level', 1)))
        level_entry.bind('<KeyRelease>', lambda e, idx=index, field='level': self._update_enemy_field(idx, field, level_entry.get()))
        
        # Row 2: Health, Mana
        ctk.CTkLabel(details_frame, text="Health:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        health_entry = ctk.CTkEntry(details_frame, width=80)
        health_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=(5, 0))
        health_entry.insert(0, str(enemy.get('health', 100)))
        health_entry.bind('<KeyRelease>', lambda e, idx=index, field='health': self._update_enemy_field(idx, field, health_entry.get()))
        
        ctk.CTkLabel(details_frame, text="Mana:").grid(row=1, column=2, sticky="w", padx=(10, 5), pady=(5, 0))
        mana_entry = ctk.CTkEntry(details_frame, width=80)
        mana_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=(5, 0))
        mana_entry.insert(0, str(enemy.get('mana', 50)))
        mana_entry.bind('<KeyRelease>', lambda e, idx=index, field='mana': self._update_enemy_field(idx, field, mana_entry.get()))
        
        # Row 3: AI Type, Position
        ctk.CTkLabel(details_frame, text="AI Type:").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        ai_menu = ctk.CTkOptionMenu(details_frame, values=["aggressive", "defensive", "tactical", "support", "berserker"])
        ai_menu.grid(row=2, column=1, sticky="ew", padx=5, pady=(5, 0))
        ai_menu.set(enemy.get('ai_type', 'aggressive'))
        ai_menu.configure(command=lambda value, idx=index: self._update_enemy_field(idx, 'ai_type', value))
        
        ctk.CTkLabel(details_frame, text="Position:").grid(row=2, column=2, sticky="w", padx=(10, 5), pady=(5, 0))
        pos_menu = ctk.CTkOptionMenu(details_frame, values=["front", "back"])
        pos_menu.grid(row=2, column=3, sticky="ew", padx=5, pady=(5, 0))
        pos_menu.set(enemy.get('position', 'front'))
        pos_menu.configure(command=lambda value, idx=index: self._update_enemy_field(idx, 'position', value))
    
    def _add_enemy(self):
        """Adds a new enemy to the combat."""
        new_enemy = {
            "name": "New Enemy",
            "level": 1,
            "health": 80,
            "max_health": 80,
            "mana": 30,
            "max_mana": 30,
            "stats": {
                "strength": 10,
                "agility": 10,
                "intelligence": 8,
                "vitality": 10,
                "luck": 8
            },
            "skills": ["basic_attack"],
            "ai_type": "aggressive",
            "position": "front"
        }
        self.node.enemies.append(new_enemy)
        self._refresh_enemies_list()
    
    def _remove_enemy(self, index):
        """Removes an enemy from the combat."""
        if 0 <= index < len(self.node.enemies):
            self.node.enemies.pop(index)
            self._refresh_enemies_list()
    
    def _update_enemy_field(self, index, field, value):
        """Updates a specific field of an enemy."""
        if 0 <= index < len(self.node.enemies):
            try:
                if field in ['level', 'health', 'mana', 'max_health', 'max_mana']:
                    value = int(value) if value.isdigit() else 0
                self.node.enemies[index][field] = value
                # Update max_health when health changes
                if field == 'health':
                    self.node.enemies[index]['max_health'] = value
                # Update max_mana when mana changes
                if field == 'mana':
                    self.node.enemies[index]['max_mana'] = value
            except (ValueError, KeyError):
                pass
    
    def _refresh_allies_list(self):
        """Refreshes the allies list display."""
        # Clear existing widgets
        for widget in self.allies_frame.winfo_children():
            widget.destroy()
        
        allies = getattr(self.node, 'allies', [])
        if not allies:
            no_allies_label = ctk.CTkLabel(self.allies_frame, text="No allies configured. Click 'Add Ally' to add one.")
            no_allies_label.pack(pady=20)
    
    def _add_ally(self):
        """Adds a new ally to the combat."""
        new_ally = {
            "name": "Allied Fighter",
            "level": 1,
            "health": 70,
            "max_health": 70,
            "mana": 40,
            "max_mana": 40,
            "stats": {
                "strength": 8,
                "agility": 12,
                "intelligence": 10,
                "vitality": 8,
                "luck": 12
            },
            "skills": ["basic_attack", "heal"],
            "ai_type": "support",
            "position": "back"
        }
        self.node.allies.append(new_ally)
        self._refresh_allies_list()
    
    def _refresh_hazards_list(self):
        """Refreshes the hazards list display."""
        # Clear existing widgets
        for widget in self.hazards_frame.winfo_children():
            widget.destroy()
        
        hazards = getattr(self.node, 'environmental_hazards', [])
        if not hazards:
            no_hazards_label = ctk.CTkLabel(self.hazards_frame, text="No environmental hazards. Click 'Add Hazard' to add one.")
            no_hazards_label.pack(pady=20)
    
    def _add_hazard(self):
        """Adds a new environmental hazard."""
        new_hazard = {
            "name": "Dangerous Trap",
            "type": "damage",
            "effect": {
                "damage": 10,
                "element": "physical"
            },
            "trigger": "turn_end",
            "target": "all",
            "duration": -1,
            "description": "A hazardous environmental effect"
        }
        self.node.environmental_hazards.append(new_hazard)
        self._refresh_hazards_list()
    
    def _save_node(self):
        """Saves the combat node configuration."""
        try:
            # Update basic settings
            self.node.npc = self.npc_entry.get() or "Combat Encounter"
            self.node.text = self.desc_text.get("0.0", "end-1c") or "A fierce battle awaits!"
            
            self.node.combat_type = self.combat_type.get()
            self.node.initiative_system = self.initiative.get()
            self.node.allow_escape = self.allow_escape.get()
            self.node.escape_difficulty = int(self.escape_difficulty.get() or 10)
            self.node.formation_matters = self.formation_matters.get()
            self.node.turn_limit = int(self.turn_limit.get() or 0)
            
            # Node connections
            self.node.victory_node = self.victory_node.get()
            self.node.defeat_node = self.defeat_node.get()
            self.node.escape_node = self.escape_node.get()
            
            # Environment
            self.node.environment = self.environment.get()
            self.node.weather = self.weather.get()
            
            # Rewards
            self.node.experience_reward = int(self.experience_reward.get() or 100)
            self.node.gold_reward = int(self.gold_reward.get() or 50)
            self.node.skill_points_reward = int(self.skill_points_reward.get() or 1)
            
            # Item rewards
            try:
                item_rewards_text = self.item_rewards_text.get("0.0", "end-1c").strip()
                if item_rewards_text and not item_rewards_text.startswith("Enter item"):
                    self.node.item_rewards = json.loads(item_rewards_text)
                else:
                    self.node.item_rewards = []
            except json.JSONDecodeError:
                self.node.item_rewards = []
            
            # Advanced settings
            try:
                self.node.victory_conditions = json.loads(self.victory_conditions.get("0.0", "end-1c"))
                self.node.defeat_conditions = json.loads(self.defeat_conditions.get("0.0", "end-1c"))
                self.node.special_rules = json.loads(self.special_rules.get("0.0", "end-1c"))
            except json.JSONDecodeError:
                pass  # Keep existing values if JSON is invalid
            
            # Save state for undo
            if self.is_new_node:
                self.app._save_state_for_undo("Add Advanced Combat Node")
            else:
                self.app._save_state_for_undo("Edit Advanced Combat Node")
            
            # If this is a new node, add it to the app
            if self.is_new_node:
                # Remove placeholder if it exists
                if hasattr(self.app.canvas_manager, 'placeholder_id') and self.app.canvas_manager.placeholder_id:
                    self.app.canvas.delete(self.app.canvas_manager.placeholder_id)
                    self.app.canvas_manager.placeholder_id = None
                
                # Generate unique node ID
                while f"node_{self.app.node_id_counter}" in self.app.nodes:
                    self.app.node_id_counter += 1
                
                node_id_str = f"node_{self.app.node_id_counter}"
                self.app.node_id_counter += 1
                
                self.node.id = node_id_str
                self.app.nodes[node_id_str] = self.node
                
                # Create visual on canvas
                self.app.canvas_manager.create_node_visual(self.node)
                self.app.set_selection([node_id_str], node_id_str)
            else:
                # Update existing node visual
                self.app.canvas_manager.redraw_node(self.node.id)
            
            self.destroy()
            
        except Exception as e:
            ctk.CTkMessagebox.show_error("Error", f"Failed to save combat node: {str(e)}")
    
    def _cancel(self):
        """Cancels editing and restores original data if needed."""
        if not self.is_new_node and self.original_node_data:
            # Restore original data
            self.node.update_from_dict(self.original_node_data)
            self.app.canvas_manager.redraw_node(self.node.id)
        
        self.destroy()
    
    def _preview_combat(self):
        """Opens a preview of the combat configuration."""
        # This could open a preview window or export a test HTML
        ctk.CTkMessagebox.show_info("Preview", "Combat preview functionality could be implemented here to test the combat configuration.")