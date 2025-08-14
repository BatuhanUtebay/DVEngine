# dvge/ui/windows/preview_window.py

"""Enhanced preview window with shop, inventory, and timer interfaces."""

import tkinter as tk
import customtkinter as ctk
from ...constants import *
from ...core.preview_engine import EnhancedPreviewGameEngine


class PreviewWindow(ctk.CTkToplevel):
    """Main preview window class that handles all node types."""
    
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.app = parent_app
        self.preview_engine = EnhancedPreviewGameEngine(parent_app)
        
        self.title("Live Preview - Dialogue Venture")
        self.geometry("1400x900")
        self.transient(parent_app)
        
        # Setup callbacks
        self.preview_engine.on_node_change = self._on_node_change
        self.preview_engine.on_state_change = self._on_state_change
        self.preview_engine.on_message = self._on_message
        self.preview_engine.on_shop_open = self._on_shop_open
        self.preview_engine.on_inventory_open = self._on_inventory_open
        self.preview_engine.on_timer_start = self._on_timer_start
        
        # Timer tracking
        self.active_timer = None
        self.timer_after_id = None
        
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
        self._create_special_interfaces()
        
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
        
    def _create_special_interfaces(self):
        """Creates special interfaces for shop, inventory, and timer."""
        # Shop interface
        self.shop_window = None
        
        # Inventory interface 
        self.inventory_window = None
        
        # Timer interface
        self.timer_frame = ctk.CTkFrame(self.game_frame, fg_color=COLOR_WARNING)
        self.timer_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        self.timer_frame.grid_remove()  # Initially hidden
        
        self.timer_label = ctk.CTkLabel(
            self.timer_frame, text="Timer: 00:00", 
            font=FONT_TITLE, text_color="white"
        )
        self.timer_label.pack(pady=10)
        
    def _start_preview(self):
        """Starts the preview from the intro node."""
        if "intro" not in self.app.nodes:
            self._on_message("No 'intro' node found! Please create an intro node first.", "error")
            return
            
        self.preview_engine.start_game()
        
    def _restart_game(self):
        """Restarts the game from the beginning."""
        self._clear_timer()
        self._close_special_windows()
        self.preview_engine.start_game()
        self._clear_message()
        
    def _show_jump_dialog(self):
        """Shows dialog to jump to a specific node."""
        dialog = NodeJumpDialog(self, list(self.app.nodes.keys()))
        self.wait_window(dialog)
        
        if hasattr(dialog, 'selected_node') and dialog.selected_node:
            self._clear_timer()
            self._close_special_windows()
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
            
        # Create option buttons based on node type and options
        for i, option in enumerate(node_data.get('options', [])):
            action = option.get('action', 'navigate')
            
            if action == 'open_shop':
                btn = ctk.CTkButton(
                    self.options_frame, 
                    text=option['text'], 
                    anchor="w",
                    fg_color=COLOR_SUCCESS,
                    command=lambda idx=i: self.preview_engine.choose_option(idx)
                )
            elif action == 'open_inventory':
                btn = ctk.CTkButton(
                    self.options_frame, 
                    text=option['text'], 
                    anchor="w",
                    fg_color=COLOR_ACCENT,
                    command=lambda idx=i: self.preview_engine.choose_option(idx)
                )
            elif action == 'random_event':
                btn = ctk.CTkButton(
                    self.options_frame, 
                    text=option['text'], 
                    anchor="w",
                    fg_color=COLOR_WARNING,
                    command=lambda idx=i: self.preview_engine.choose_option(idx)
                )
            elif action == 'skip_timer':
                btn = ctk.CTkButton(
                    self.options_frame, 
                    text=option['text'], 
                    anchor="w",
                    fg_color=COLOR_ERROR,
                    command=lambda idx=i: self.preview_engine.choose_option(idx)
                )
            else:
                btn = ctk.CTkButton(
                    self.options_frame, 
                    text=option['text'], 
                    anchor="w",
                    command=lambda idx=i: self.preview_engine.choose_option(idx)
                )
            btn.pack(fill="x", pady=2)
            
        # Handle special node types
        node_type = node_data.get('node_type', 'Dialogue')
        if node_type == 'DiceRollNode' and node_data.get('dice_data'):
            self._create_dice_roll_button(node_data['dice_data'])
        elif node_type == 'CombatNode' and node_data.get('combat_data'):
            self._create_combat_button(node_data['combat_data'])
        elif node_type == 'RandomOutcome':
            # Auto-continue after showing outcome
            self.after(2000, self.preview_engine.complete_pending_navigation)
            
    def _on_shop_open(self, shop_data):
        """Called when shop should be opened."""
        if self.shop_window:
            self.shop_window.destroy()
            
        self.shop_window = ShopInterface(self, shop_data, self.preview_engine)
        
    def _on_inventory_open(self, inventory_data):
        """Called when inventory should be opened."""
        if self.inventory_window:
            self.inventory_window.destroy()
            
        self.inventory_window = InventoryInterface(self, inventory_data, self.preview_engine)
        
    def _on_timer_start(self, duration_seconds, next_node, show_countdown):
        """Called when timer should start."""
        if show_countdown:
            self.timer_frame.grid()
            self._start_timer_countdown(duration_seconds, next_node)
        else:
            # Just wait without showing countdown
            self.timer_after_id = self.after(
                duration_seconds * 1000, 
                lambda: self.preview_engine.timer_expired(next_node)
            )
            
    def _start_timer_countdown(self, duration_seconds, next_node):
        """Starts a visual countdown timer."""
        self.timer_remaining = duration_seconds
        self.timer_next_node = next_node
        self._update_timer_display()
        
    def _update_timer_display(self):
        """Updates the timer display."""
        if self.timer_remaining <= 0:
            self.timer_frame.grid_remove()
            self.preview_engine.timer_expired(self.timer_next_node)
            return
            
        minutes = self.timer_remaining // 60
        seconds = self.timer_remaining % 60
        self.timer_label.configure(text=f"Timer: {minutes:02d}:{seconds:02d}")
        
        self.timer_remaining -= 1
        self.timer_after_id = self.after(1000, self._update_timer_display)
        
    def _clear_timer(self):
        """Clears any active timer."""
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.timer_frame.grid_remove()
        
    def _close_special_windows(self):
        """Closes any open special windows."""
        if self.shop_window:
            self.shop_window.destroy()
            self.shop_window = None
        if self.inventory_window:
            self.inventory_window.destroy()
            self.inventory_window = None
            
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


class ShopInterface(ctk.CTkToplevel):
    """Shop interface window."""
    
    def __init__(self, parent, shop_data, engine):
        super().__init__(parent)
        self.shop_data = shop_data
        self.engine = engine
        
        self.title("🏪 Shop")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        self._update_display()
        
    def _setup_ui(self):
        """Sets up the shop interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame, text="🏪 Shop", 
            font=FONT_TITLE, text_color=COLOR_SUCCESS
        ).grid(row=0, column=0, sticky="w")
        
        self.currency_label = ctk.CTkLabel(
            header_frame, text="Gold: 0", 
            font=FONT_PROPERTIES_LABEL
        )
        self.currency_label.grid(row=0, column=1, sticky="e")
        
        # Tabs
        self.tab_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.tab_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0,10))
        
        self.buy_tab_btn = ctk.CTkButton(
            self.tab_frame, text="Buy Items", 
            command=lambda: self._switch_tab('buy'),
            fg_color=COLOR_SUCCESS
        )
        self.buy_tab_btn.pack(side="left", padx=(0,10))
        
        self.sell_tab_btn = ctk.CTkButton(
            self.tab_frame, text="Sell Items", 
            command=lambda: self._switch_tab('sell')
        )
        self.sell_tab_btn.pack(side="left")
        
        # Content area
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0,10))
        
        # Close button
        ctk.CTkButton(
            self, text="Close Shop", 
            command=self._close_shop,
            fg_color=COLOR_ERROR
        ).grid(row=3, column=0, padx=20, pady=(0,20))
        
        self.current_tab = 'buy'
        
    def _switch_tab(self, tab):
        """Switches between buy and sell tabs."""
        self.current_tab = tab
        
        if tab == 'buy':
            self.buy_tab_btn.configure(fg_color=COLOR_SUCCESS)
            self.sell_tab_btn.configure(fg_color=COLOR_SECONDARY_FRAME)
        else:
            self.buy_tab_btn.configure(fg_color=COLOR_SECONDARY_FRAME)
            self.sell_tab_btn.configure(fg_color=COLOR_SUCCESS)
            
        self._update_display()
        
    def _update_display(self):
        """Updates the shop display."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # Update currency display
        currency_var = self.shop_data['currency_variable']
        current_currency = self.engine.variables.get(currency_var, 0)
        self.currency_label.configure(text=f"{currency_var.title()}: {current_currency}")
        
        if self.current_tab == 'buy':
            self._show_buy_items()
        else:
            self._show_sell_items()
            
    def _show_buy_items(self):
        """Shows items available for purchase."""
        for item in self.shop_data['items_for_sale']:
            item_frame = ctk.CTkFrame(self.content_frame)
            item_frame.pack(fill="x", pady=5, padx=10)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Item info
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
            
            ctk.CTkLabel(
                info_frame, text=item.get('name', 'Unknown Item'), 
                font=FONT_PROPERTIES_LABEL
            ).pack(anchor="w")
            
            if item.get('description'):
                ctk.CTkLabel(
                    info_frame, text=item['description'], 
                    font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
                ).pack(anchor="w")
                
            # Price and buy button
            price_label = ctk.CTkLabel(
                item_frame, text=f"Price: {item.get('price', 0)}", 
                font=FONT_PROPERTIES_ENTRY
            )
            price_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            
            buy_btn = ctk.CTkButton(
                item_frame, text="Buy", 
                command=lambda i=item: self._buy_item(i),
                fg_color=COLOR_SUCCESS
            )
            buy_btn.grid(row=1, column=1, padx=10, pady=5, sticky="e")
            
    def _show_sell_items(self):
        """Shows items available for sale."""
        sellable_items = []
        
        # Find items player can sell
        for buy_item in self.shop_data['items_to_buy']:
            if any(inv_item.get('name') == buy_item.get('name') for inv_item in self.engine.player_inventory):
                sellable_items.append(buy_item)
                
        if not sellable_items:
            ctk.CTkLabel(
                self.content_frame, text="You have no items to sell here.", 
                font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
            ).pack(pady=20)
            return
            
        for item in sellable_items:
            item_frame = ctk.CTkFrame(self.content_frame)
            item_frame.pack(fill="x", pady=5, padx=10)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Item info
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
            
            ctk.CTkLabel(
                info_frame, text=item.get('name', 'Unknown Item'), 
                font=FONT_PROPERTIES_LABEL
            ).pack(anchor="w")
            
            if item.get('description'):
                ctk.CTkLabel(
                    info_frame, text=item['description'], 
                    font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
                ).pack(anchor="w")
                
            # Price and sell button
            price_label = ctk.CTkLabel(
                item_frame, text=f"Price: {item.get('price', 0)}", 
                font=FONT_PROPERTIES_ENTRY
            )
            price_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
            
            sell_btn = ctk.CTkButton(
                item_frame, text="Sell", 
                command=lambda i=item: self._sell_item(i),
                fg_color=COLOR_WARNING
            )
            sell_btn.grid(row=1, column=1, padx=10, pady=5, sticky="e")
            
    def _buy_item(self, item):
        """Handles buying an item."""
        success = self.engine.buy_item(
            item.get('name', ''), 
            item.get('price', 0), 
            self.shop_data['currency_variable']
        )
        if success:
            self._update_display()
            
    def _sell_item(self, item):
        """Handles selling an item."""
        success = self.engine.sell_item(
            item.get('name', ''), 
            item.get('price', 0), 
            self.shop_data['currency_variable']
        )
        if success:
            self._update_display()
            
    def _close_shop(self):
        """Closes the shop."""
        self.engine.close_shop(self.shop_data.get('continue_node'))
        self.destroy()


class InventoryInterface(ctk.CTkToplevel):
    """Inventory interface window."""
    
    def __init__(self, parent, inventory_data, engine):
        super().__init__(parent)
        self.inventory_data = inventory_data
        self.engine = engine
        
        self.title("🎒 Inventory")
        self.geometry("700x600")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()
        self._update_display()
        
    def _setup_ui(self):
        """Sets up the inventory interface."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            header_frame, text="🎒 Inventory", 
            font=FONT_TITLE, text_color=COLOR_ACCENT
        ).pack()
        
        # Notebook for tabs
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,10))
        
        # Items tab
        self.notebook.add("Items")
        self.items_frame = ctk.CTkScrollableFrame(self.notebook.tab("Items"))
        self.items_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crafting tab
        self.notebook.add("Crafting")
        self.crafting_frame = ctk.CTkScrollableFrame(self.notebook.tab("Crafting"))
        self.crafting_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Close button
        ctk.CTkButton(
            self, text="Close Inventory", 
            command=self._close_inventory,
            fg_color=COLOR_ERROR
        ).grid(row=2, column=0, padx=20, pady=(0,20))
        
    def _update_display(self):
        """Updates the inventory display."""
        self._show_items()
        self._show_crafting()
        
    def _show_items(self):
        """Shows player's items."""
        # Clear items
        for widget in self.items_frame.winfo_children():
            widget.destroy()
            
        if not self.engine.player_inventory:
            ctk.CTkLabel(
                self.items_frame, text="Your inventory is empty.", 
                font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
            ).pack(pady=20)
            return
            
        for item in self.engine.player_inventory:
            item_frame = ctk.CTkFrame(self.items_frame)
            item_frame.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(
                item_frame, text=item.get('name', 'Unknown Item'), 
                font=FONT_PROPERTIES_LABEL
            ).pack(anchor="w", padx=10, pady=(10,5))
            
            if item.get('description'):
                ctk.CTkLabel(
                    item_frame, text=item['description'], 
                    font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
                ).pack(anchor="w", padx=10, pady=(0,10))
                
    def _show_crafting(self):
        """Shows crafting recipes."""
        # Clear crafting
        for widget in self.crafting_frame.winfo_children():
            widget.destroy()
            
        if not self.inventory_data.get('crafting_recipes'):
            ctk.CTkLabel(
                self.crafting_frame, text="No crafting recipes available.", 
                font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
            ).pack(pady=20)
            return
            
        for recipe in self.inventory_data['crafting_recipes']:
            recipe_frame = ctk.CTkFrame(self.crafting_frame)
            recipe_frame.pack(fill="x", pady=5, padx=5)
            recipe_frame.grid_columnconfigure(0, weight=1)
            
            # Recipe info
            info_frame = ctk.CTkFrame(recipe_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
            
            ctk.CTkLabel(
                info_frame, text=recipe.get('name', 'Unknown Recipe'), 
                font=FONT_PROPERTIES_LABEL
            ).pack(anchor="w")
            
            ingredients_text = f"Requires: {', '.join(recipe.get('ingredients', []))}"
            ctk.CTkLabel(
                info_frame, text=ingredients_text, 
                font=FONT_PROPERTIES_ENTRY, text_color=COLOR_TEXT_MUTED
            ).pack(anchor="w")
            
            result_text = f"Creates: {recipe.get('result', 'Unknown Item')}"
            ctk.CTkLabel(
                info_frame, text=result_text, 
                font=FONT_PROPERTIES_ENTRY, text_color=COLOR_SUCCESS
            ).pack(anchor="w")
            
            # Check if can craft
            can_craft = self._can_craft_recipe(recipe)
            
            craft_btn = ctk.CTkButton(
                recipe_frame, 
                text="Craft" if can_craft else "Missing Items", 
                command=lambda r=recipe: self._craft_item(r),
                fg_color=COLOR_SUCCESS if can_craft else COLOR_ERROR,
                state="normal" if can_craft else "disabled"
            )
            craft_btn.grid(row=0, column=1, padx=10, pady=5)
            
    def _can_craft_recipe(self, recipe):
        """Checks if player can craft a recipe."""
        ingredients = recipe.get('ingredients', [])
        inventory_items = [item.get('name') for item in self.engine.player_inventory]
        
        return all(ingredient in inventory_items for ingredient in ingredients)
        
    def _craft_item(self, recipe):
        """Handles crafting an item."""
        success = self.engine.craft_item(
            recipe.get('name', ''),
            recipe.get('ingredients', []),
            recipe.get('result', '')
        )
        if success:
            self._update_display()
            
    def _close_inventory(self):
        """Closes the inventory."""
        self.engine.close_inventory(self.inventory_data.get('continue_node'))
        self.destroy()


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


# Enhanced preview window class for backward compatibility
class EnhancedPreviewWindow(PreviewWindow):
    """Enhanced preview window alias for backward compatibility."""
    pass