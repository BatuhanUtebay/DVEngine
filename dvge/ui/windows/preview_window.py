# dvge/ui/windows/preview_window.py

"""Live preview window for testing games within the editor."""

import tkinter as tk
import customtkinter as ctk
from ...constants import *
from ...core.preview_engine import PreviewGameEngine


class PreviewWindow(ctk.CTkToplevel):
    """Window for live game preview with debug tools."""
    
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.app = parent_app
        self.preview_engine = PreviewGameEngine(parent_app)
        
        self.title("Live Preview - Dialogue Venture")
        self.geometry("1200x800")
        self.transient(parent_app)
        
        # Setup callbacks
        self.preview_engine.on_node_change = self._on_node_change
        self.preview_engine.on_state_change = self._on_state_change
        self.preview_engine.on_message = self._on_message
        
        self._setup_ui()
        self._start_preview()
        
    def _setup_ui(self):
        """Sets up the preview window UI."""
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_toolbar()
        self._create_game_area()
        self._create_debug_panel()
        
    def _create_toolbar(self):
        """Creates the preview control toolbar."""
        toolbar = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME, height=50)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10,5))
        toolbar.grid_columnconfigure(1, weight=1)
        
        # Control buttons
        controls_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        controls_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.restart_btn = ctk.CTkButton(
            controls_frame, text="🔄 Restart", width=80,
            command=self._restart_game
        )
        self.restart_btn.pack(side="left", padx=(0,5))
        
        self.jump_btn = ctk.CTkButton(
            controls_frame, text="🎯 Jump to Node", width=120,
            command=self._show_jump_dialog
        )
        self.jump_btn.pack(side="left", padx=5)
        
        # Current node display
        self.current_node_label = ctk.CTkLabel(
            toolbar, text="Current: intro", 
            font=FONT_PROPERTIES_LABEL
        )
        self.current_node_label.grid(row=0, column=1, padx=10)
        
        # Close button
        ctk.CTkButton(
            toolbar, text="❌ Close Preview", width=120,
            command=self.destroy, fg_color=COLOR_ERROR
        ).grid(row=0, column=2, sticky="e", padx=10, pady=5)
        
    def _create_game_area(self):
        """Creates the main game display area."""
        self.game_frame = ctk.CTkFrame(self, fg_color=COLOR_SECONDARY_FRAME)
        self.game_frame.grid(row=1, column=0, sticky="nsew", padx=(10,5), pady=5)
        self.game_frame.grid_columnconfigure(0, weight=1)
        self.game_frame.grid_rowconfigure(1, weight=1)
        
        # NPC/Chapter header
        self.npc_label = ctk.CTkLabel(
            self.game_frame, text="Narrator", 
            font=FONT_TITLE, text_color=COLOR_ACCENT
        )
        self.npc_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        
        # Dialogue text
        self.dialogue_text = ctk.CTkTextbox(
            self.game_frame, wrap="word", 
            font=FONT_DIALOGUE, height=200,
            activate_scrollbars=False
        )
        self.dialogue_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Options frame
        self.options_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10,20))
        
        # Messages area
        self.messages_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent", height=60)
        self.messages_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0,20))
        
        self.message_label = ctk.CTkLabel(
            self.messages_frame, text="", 
            font=FONT_PROPERTIES_ENTRY, wraplength=500
        )
        self.message_label.pack(pady=10)
        
    def _create_debug_panel(self):
        """Creates the debug information panel."""
        debug_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        debug_frame.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=5)
        debug_frame.grid_columnconfigure(0, weight=1)
        debug_frame.grid_rowconfigure(3, weight=1)
        
        # Debug title
        ctk.CTkLabel(
            debug_frame, text="Debug Info", 
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ACCENT
        ).grid(row=0, column=0, padx=15, pady=(15,10), sticky="w")
        
        # Node history
        history_frame = ctk.CTkFrame(debug_frame, fg_color="transparent")
        history_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        ctk.CTkLabel(
            history_frame, text="Path Taken:", 
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w")
        
        self.history_text = ctk.CTkTextbox(
            history_frame, height=80, font=("Courier", 10)
        )
        self.history_text.pack(fill="x", pady=(5,0))
        
        # Quick stats
        stats_frame = ctk.CTkFrame(debug_frame, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=5)
        
        ctk.CTkLabel(
            stats_frame, text="Quick Stats:", 
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w")
        
        self.stats_text = ctk.CTkTextbox(
            stats_frame, height=100, font=("Courier", 10)
        )
        self.stats_text.pack(fill="x", pady=(5,0))
        
        # Detailed state
        ctk.CTkLabel(
            debug_frame, text="Full State:", 
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=3, column=0, padx=15, pady=(10,5), sticky="nw")
        
        self.debug_text = ctk.CTkTextbox(
            debug_frame, font=("Courier", 9)
        )
        self.debug_text.grid(row=4, column=0, sticky="nsew", padx=15, pady=(0,15))
        
    def _start_preview(self):
        """Starts the preview from the intro node."""
        if "intro" not in self.app.nodes:
            self._on_message("No 'intro' node found! Please create an intro node first.", "error")
            return
            
        self.preview_engine.start_game()
        
    def _restart_game(self):
        """Restarts the game from the beginning."""
        self.preview_engine.start_game()
        self._clear_message()
        
    def _show_jump_dialog(self):
        """Shows dialog to jump to a specific node."""
        dialog = NodeJumpDialog(self, list(self.app.nodes.keys()))
        self.wait_window(dialog)
        
        if hasattr(dialog, 'selected_node') and dialog.selected_node:
            self.preview_engine.jump_to_node(dialog.selected_node)
            
    def _on_node_change(self, node_data):
        """Called when the current node changes."""
        # Update header
        npc_text = node_data['npc']
        if node_data.get('chapter'):
            npc_text += f" - {node_data['chapter']}"
        self.npc_label.configure(text=npc_text)
        
        # Update current node display
        self.current_node_label.configure(text=f"Current: {node_data['id']}")
        
        # Update dialogue text
        self.dialogue_text.delete("1.0", "end")
        self.dialogue_text.insert("1.0", node_data['text'])
        
        # Clear options
        for widget in self.options_frame.winfo_children():
            widget.destroy()
            
        # Create option buttons or special node controls
        if node_data['node_type'] == 'DiceRollNode':
            self._create_dice_roll_button(node_data['dice_data'])
        elif node_data['node_type'] == 'CombatNode':
            self._create_combat_button(node_data['combat_data'])
        elif node_data['node_type'] == 'EndGame':
            # Game over, no options
            pass
        else:
            # Regular dialogue options
            for i, option in enumerate(node_data['options']):
                btn = ctk.CTkButton(
                    self.options_frame, 
                    text=f"{i+1}. {option['text']}", 
                    anchor="w",
                    command=lambda idx=i: self.preview_engine.choose_option(idx)
                )
                btn.pack(fill="x", pady=2)
                
        # Handle auto-advance
        if node_data.get('auto_advance') and node_data['options']:
            delay = node_data.get('auto_advance_delay', 0) * 1000
            if delay > 0:
                self.after(int(delay), lambda: self.preview_engine.choose_option(0))
                
    def _create_dice_roll_button(self, dice_data):
        """Creates dice roll button for DiceRollNode."""
        if not dice_data:
            return
            
        btn_text = f"🎲 Roll {dice_data['num_dice']}d{dice_data['num_sides']} (Need {dice_data['success_threshold']}+)"
        btn = ctk.CTkButton(
            self.options_frame, text=btn_text,
            command=self.preview_engine.perform_dice_roll,
            fg_color=COLOR_WARNING
        )
        btn.pack(fill="x", pady=5)
        
    def _create_combat_button(self, combat_data):
        """Creates combat button for CombatNode."""
        if not combat_data:
            return
            
        btn = ctk.CTkButton(
            self.options_frame, text="⚔️ Begin Combat",
            command=self.preview_engine.perform_combat,
            fg_color=COLOR_ERROR
        )
        btn.pack(fill="x", pady=5)
        
    def _on_state_change(self, debug_state):
        """Called when game state changes."""
        # Update history
        self.history_text.delete("1.0", "end")
        history = " → ".join(debug_state['history'][-10:])  # Last 10 nodes
        if len(debug_state['history']) > 10:
            history = "... → " + history
        self.history_text.insert("1.0", history)
        
        # Update quick stats
        self.stats_text.delete("1.0", "end")
        quick_stats = []
        
        # Player stats
        for stat, value in debug_state['player_stats'].items():
            quick_stats.append(f"{stat}: {value}")
            
        # Variables
        for var, value in debug_state['variables'].items():
            quick_stats.append(f"{var}: {value}")
            
        # Active flags
        active_flags = [name for name, value in debug_state['story_flags'].items() if value]
        if active_flags:
            quick_stats.append(f"Flags: {', '.join(active_flags[:3])}")
            
        self.stats_text.insert("1.0", "\n".join(quick_stats))
        
        # Update full debug info
        self.debug_text.delete("1.0", "end")
        debug_info = f"""INVENTORY:
{chr(10).join(f"• {item['name']}" for item in debug_state['inventory'])}

FLAGS:
{chr(10).join(f"• {name}: {value}" for name, value in debug_state['story_flags'].items())}

QUESTS:
{chr(10).join(f"• {qid}: {quest['state']}" for qid, quest in debug_state['quests'].items())}"""
        
        self.debug_text.insert("1.0", debug_info)
        
    def _on_message(self, message, msg_type="info"):
        """Called when a message should be displayed."""
        color_map = {
            "info": COLOR_TEXT,
            "success": COLOR_SUCCESS, 
            "warning": COLOR_WARNING,
            "error": COLOR_ERROR
        }
        
        self.message_label.configure(
            text=message, 
            text_color=color_map.get(msg_type, COLOR_TEXT)
        )
        
        # Auto-clear after 5 seconds
        self.after(5000, self._clear_message)
        
    def _clear_message(self):
        """Clears the message display."""
        self.message_label.configure(text="")


class NodeJumpDialog(ctk.CTkToplevel):
    """Dialog for jumping to a specific node."""
    
    def __init__(self, parent, node_list):
        super().__init__(parent)
        self.selected_node = None
        
        self.title("Jump to Node")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        self.geometry(f"+{parent.winfo_x() + 50}+{parent.winfo_y() + 50}")
        
        self._setup_ui(node_list)
        
    def _setup_ui(self, node_list):
        """Sets up the dialog UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(
            self, text="Select Node to Jump To:", 
            font=FONT_PROPERTIES_LABEL
        ).grid(row=0, column=0, padx=20, pady=(20,10))
        
        # Node list
        self.listbox = tk.Listbox(
            self, bg=COLOR_SECONDARY_FRAME, fg=COLOR_TEXT,
            selectbackground=COLOR_ACCENT, font=FONT_PROPERTIES_ENTRY,
            borderwidth=0, highlightthickness=1, 
            highlightcolor=COLOR_ACCENT
        )
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Populate list
        for node_id in sorted(node_list):
            self.listbox.insert("end", node_id)
            
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0,20))
        button_frame.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkButton(
            button_frame, text="Jump", 
            command=self._on_jump
        ).grid(row=0, column=0, padx=(0,5), pady=10, sticky="ew")
        
        ctk.CTkButton(
            button_frame, text="Cancel", 
            command=self.destroy,
            fg_color=COLOR_ERROR
        ).grid(row=0, column=1, padx=(5,0), pady=10, sticky="ew")
        
        # Bind double-click
        self.listbox.bind("<Double-Button-1>", lambda e: self._on_jump())
        
    def _on_jump(self):
        """Handles jump button click."""
        selection = self.listbox.curselection()
        if selection:
            self.selected_node = self.listbox.get(selection[0])
            self.destroy()