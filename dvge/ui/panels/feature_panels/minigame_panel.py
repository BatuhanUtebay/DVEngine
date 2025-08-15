import customtkinter as ctk
from ....constants import *


class MinigamePanel(ctk.CTkFrame):
    """Panel for configuring minigames."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        self._setup_layout()
        self._create_widgets()
        
    def _setup_layout(self):
        """Sets up the panel layout."""
        self.grid_columnconfigure(0, weight=1)
        
    def _create_widgets(self):
        """Creates minigame configuration widgets."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        title_frame.pack(fill="x", pady=5, padx=5)
        
        ctk.CTkLabel(
            title_frame, text="🎮 Minigame Configuration",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_SUCCESS
        ).pack(padx=10, pady=10)
        
        # Game Type Selection
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.pack(fill="x", pady=5, padx=10)
        type_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            type_frame, text="Game Type:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        self.game_type_combo = ctk.CTkComboBox(
            type_frame,
            values=["Card Game", "Dice Game", "Reaction Test", "Memory Game", "Betting"],
            font=FONT_PROPERTIES_ENTRY,
            command=self._on_game_type_change
        )
        self.game_type_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Dynamic settings area
        self.settings_container = ctk.CTkFrame(self, fg_color=COLOR_SECONDARY_FRAME)
        self.settings_container.pack(fill="both", expand=True, pady=5, padx=10)
        
        # Entry fee and rewards
        rewards_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        rewards_frame.pack(fill="x", pady=5, padx=10)
        rewards_frame.grid_columnconfigure((0,1), weight=1)
        
        # Entry fee
        fee_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        fee_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            fee_frame, text="Entry Fee:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.entry_fee = ctk.CTkEntry(fee_frame, placeholder_text="0", width=80)
        self.entry_fee.pack(side="left", padx=5)
        
        # Base reward
        reward_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        reward_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            reward_frame, text="Base Reward:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.base_reward = ctk.CTkEntry(reward_frame, placeholder_text="50", width=80)
        self.base_reward.pack(side="left", padx=5)
        
        # Initialize with card game
        self._show_card_game_settings()
        
    def _on_game_type_change(self, choice):
        """Handles game type selection change."""
        for widget in self.settings_container.winfo_children():
            widget.destroy()
            
        if choice == "Card Game":
            self._show_card_game_settings()
        elif choice == "Dice Game":
            self._show_dice_game_settings()
        elif choice == "Reaction Test":
            self._show_reaction_settings()
        elif choice == "Memory Game":
            self._show_memory_settings()
        elif choice == "Betting":
            self._show_betting_settings()
            
    def _show_card_game_settings(self):
        """Shows card game specific settings."""
        ctk.CTkLabel(
            self.settings_container,
            text="Higher/Lower Card Game",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        settings_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        self.streak_bonus = ctk.CTkCheckBox(
            settings_frame, text="Enable Streak Bonuses",
            font=FONT_PROPERTIES_ENTRY
        )
        self.streak_bonus.pack(anchor="w", pady=5)
        
        self.deck_size = ctk.CTkSlider(
            settings_frame, from_=20, to=52,
            number_of_steps=32
        )
        self.deck_size.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            settings_frame, text="Deck Size: 52 cards",
            font=FONT_PROPERTIES_ENTRY
        ).pack()
        
    def _show_dice_game_settings(self):
        """Shows dice game specific settings."""
        ctk.CTkLabel(
            self.settings_container,
            text="Dice Betting Game",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        settings_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        dice_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        dice_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            dice_frame, text="Number of Dice:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.num_dice = ctk.CTkEntry(dice_frame, placeholder_text="2", width=60)
        self.num_dice.pack(side="left", padx=5)
        
        self.house_edge = ctk.CTkSlider(
            settings_frame, from_=0, to=0.1,
            number_of_steps=10
        )
        self.house_edge.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            settings_frame, text="House Edge: 2%",
            font=FONT_PROPERTIES_ENTRY
        ).pack()
        
    def _show_reaction_settings(self):
        """Shows reaction game settings."""
        ctk.CTkLabel(
            self.settings_container,
            text="Quick-Time Reaction Test",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        settings_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        timing_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        timing_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            timing_frame, text="Target Time (sec):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.target_time = ctk.CTkEntry(timing_frame, placeholder_text="2.5", width=80)
        self.target_time.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            settings_frame, text="Perfect Tolerance: ±0.1 sec",
            font=FONT_PROPERTIES_ENTRY
        ).pack(pady=5)
        
        ctk.CTkLabel(
            settings_frame, text="Good Tolerance: ±0.5 sec",
            font=FONT_PROPERTIES_ENTRY
        ).pack(pady=5)
        
    def _show_memory_settings(self):
        """Shows memory game settings."""
        ctk.CTkLabel(
            self.settings_container,
            text="Memory Sequence Game",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        settings_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        self.sequence_length = ctk.CTkSlider(
            settings_frame, from_=3, to=10,
            number_of_steps=7
        )
        self.sequence_length.pack(fill="x", pady=5)
        
        self.seq_label = ctk.CTkLabel(
            settings_frame, text="Sequence Length: 5",
            font=FONT_PROPERTIES_ENTRY
        )
        self.seq_label.pack()
        
        self.sequence_length.configure(
            command=lambda v: self.seq_label.configure(
                text=f"Sequence Length: {int(v)}"
            )
        )
        
    def _show_betting_settings(self):
        """Shows betting game settings."""
        ctk.CTkLabel(
            self.settings_container,
            text="Betting/Gambling Game",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        settings_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        settings_frame.pack(fill="x", padx=20, pady=10)
        
        self.min_bet = ctk.CTkEntry(
            settings_frame, placeholder_text="Min bet: 10"
        )
        self.min_bet.pack(fill="x", pady=5, padx=20)
        
        self.max_bet = ctk.CTkEntry(
            settings_frame, placeholder_text="Max bet: 1000"
        )
        self.max_bet.pack(fill="x", pady=5, padx=20)
        
        self.allow_all_in = ctk.CTkCheckBox(
            settings_frame, text="Allow All-In Betting",
            font=FONT_PROPERTIES_ENTRY
        )
        self.allow_all_in.pack(pady=5)