import customtkinter as ctk
from ....constants import *
from ....features.puzzle_mechanics import PuzzleType


class PuzzlePanel(ctk.CTkFrame):
    """Panel for configuring puzzles and riddles."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.current_puzzle = None
        
        self._setup_layout()
        self._create_widgets()
        
    def _setup_layout(self):
        """Sets up the panel layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
    def _create_widgets(self):
        """Creates puzzle configuration widgets."""
        # Title
        title_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(
            title_frame, text="🧩 Puzzle Configuration",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_WARNING
        ).pack(padx=10, pady=10)
        
        # Puzzle Type Selection
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        type_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            type_frame, text="Puzzle Type:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        self.puzzle_type_combo = ctk.CTkComboBox(
            type_frame,
            values=["Riddle", "Sequence", "Cipher", "Memory", "Logic", "Pattern"],
            font=FONT_PROPERTIES_ENTRY,
            command=self._on_puzzle_type_change
        )
        self.puzzle_type_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Puzzle Settings
        settings_frame = ctk.CTkFrame(self, fg_color=COLOR_SECONDARY_FRAME)
        settings_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # General settings
        general_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        general_frame.pack(fill="x", padx=10, pady=10)
        general_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            general_frame, text="Attempts Allowed:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.attempts_spinner = ctk.CTkEntry(general_frame, placeholder_text="3", width=60)
        self.attempts_spinner.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(
            general_frame, text="Hint Cost:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.hint_cost_entry = ctk.CTkEntry(general_frame, placeholder_text="10 gold", width=100)
        self.hint_cost_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(
            general_frame, text="Skip Cost:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.skip_cost_entry = ctk.CTkEntry(general_frame, placeholder_text="50 gold", width=100)
        self.skip_cost_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ctk.CTkLabel(
            general_frame, text="Intelligence Bypass:",
            font=FONT_PROPERTIES_ENTRY
        ).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        self.int_bypass_entry = ctk.CTkEntry(general_frame, placeholder_text="20", width=60)
        self.int_bypass_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Dynamic puzzle content area
        self.puzzle_content_frame = ctk.CTkFrame(settings_frame, fg_color=COLOR_PRIMARY_FRAME)
        self.puzzle_content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize with riddle
        self._show_riddle_content()
        
        # Rewards and Penalties
        rewards_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        rewards_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        rewards_frame.grid_columnconfigure((0,1), weight=1)
        
        # Success rewards
        success_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        success_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            success_frame, text="Success Rewards:",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_SUCCESS
        ).pack(anchor="w")
        
        self.rewards_text = ctk.CTkTextbox(success_frame, height=60)
        self.rewards_text.pack(fill="x", pady=5)
        
        # Failure penalties
        failure_frame = ctk.CTkFrame(rewards_frame, fg_color="transparent")
        failure_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            failure_frame, text="Failure Penalties:",
            font=FONT_PROPERTIES_LABEL, text_color=COLOR_ERROR
        ).pack(anchor="w")
        
        self.penalties_text = ctk.CTkTextbox(failure_frame, height=60)
        self.penalties_text.pack(fill="x", pady=5)
        
    def _on_puzzle_type_change(self, choice):
        """Handles puzzle type change."""
        # Clear current content
        for widget in self.puzzle_content_frame.winfo_children():
            widget.destroy()
            
        if choice == "Riddle":
            self._show_riddle_content()
        elif choice == "Sequence":
            self._show_sequence_content()
        elif choice == "Cipher":
            self._show_cipher_content()
        elif choice == "Memory":
            self._show_memory_content()
        elif choice == "Logic":
            self._show_logic_content()
        elif choice == "Pattern":
            self._show_pattern_content()
            
    def _show_riddle_content(self):
        """Shows riddle configuration."""
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Riddle Configuration",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        # Riddle text
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Riddle Text:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.riddle_text = ctk.CTkTextbox(self.puzzle_content_frame, height=80)
        self.riddle_text.pack(fill="x", padx=10, pady=5)
        
        # Answer
        answer_frame = ctk.CTkFrame(self.puzzle_content_frame, fg_color="transparent")
        answer_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            answer_frame, text="Answer:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.riddle_answer = ctk.CTkEntry(answer_frame, placeholder_text="The correct answer")
        self.riddle_answer.pack(side="left", fill="x", expand=True, padx=5)
        
        # Hints
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Hints (one per line):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.hints_text = ctk.CTkTextbox(self.puzzle_content_frame, height=60)
        self.hints_text.pack(fill="x", padx=10, pady=5)
        
    def _show_sequence_content(self):
        """Shows sequence puzzle configuration."""
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Sequence Puzzle",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        # Sequence input
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Full Sequence (comma-separated):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.sequence_entry = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="1, 2, 4, 8, 16, 32, 64"
        )
        self.sequence_entry.pack(fill="x", padx=10, pady=5)
        
        # Missing positions
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Positions to Hide (comma-separated, 0-indexed):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.missing_pos_entry = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="3, 5"
        )
        self.missing_pos_entry.pack(fill="x", padx=10, pady=5)
        
        # Pattern hint
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Pattern Hint:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.pattern_hint = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="Each number is double the previous"
        )
        self.pattern_hint.pack(fill="x", padx=10, pady=5)
        
    def _show_cipher_content(self):
        """Shows cipher puzzle configuration."""
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Cipher Puzzle",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        # Cipher type
        cipher_frame = ctk.CTkFrame(self.puzzle_content_frame, fg_color="transparent")
        cipher_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            cipher_frame, text="Cipher Type:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.cipher_type = ctk.CTkComboBox(
            cipher_frame,
            values=["Caesar", "Reverse", "Substitution", "Atbash"],
            width=150
        )
        self.cipher_type.set("Caesar")
        self.cipher_type.pack(side="left", padx=5)
        
        # Original text
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Original Text:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.original_text = ctk.CTkTextbox(self.puzzle_content_frame, height=60)
        self.original_text.pack(fill="x", padx=10, pady=5)
        
        # Encrypted text (auto-generated or manual)
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Encrypted Text:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.encrypted_text = ctk.CTkTextbox(self.puzzle_content_frame, height=60)
        self.encrypted_text.pack(fill="x", padx=10, pady=5)
        
        # Auto-encrypt button
        ctk.CTkButton(
            self.puzzle_content_frame,
            text="Auto-Encrypt",
            command=self._auto_encrypt,
            height=28
        ).pack(pady=5)
        
    def _show_memory_content(self):
        """Shows memory puzzle configuration."""
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Memory Puzzle (Simon Says Style)",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        # Sequence length
        length_frame = ctk.CTkFrame(self.puzzle_content_frame, fg_color="transparent")
        length_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            length_frame, text="Sequence Length:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.memory_length_slider = ctk.CTkSlider(
            length_frame, from_=3, to=10,
            number_of_steps=7, width=200
        )
        self.memory_length_slider.set(5)
        self.memory_length_slider.pack(side="left", padx=10)
        
        self.memory_length_label = ctk.CTkLabel(
            length_frame, text="5",
            font=FONT_PROPERTIES_ENTRY
        )
        self.memory_length_label.pack(side="left", padx=5)
        
        self.memory_length_slider.configure(
            command=lambda v: self.memory_length_label.configure(text=str(int(v)))
        )
        
        # Display time
        time_frame = ctk.CTkFrame(self.puzzle_content_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            time_frame, text="Display Time (ms):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.display_time_entry = ctk.CTkEntry(
            time_frame, placeholder_text="3000", width=100
        )
        self.display_time_entry.pack(side="left", padx=5)
        
        # Color/Symbol options
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Elements (comma-separated):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.memory_elements = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="Red, Blue, Green, Yellow, Purple"
        )
        self.memory_elements.pack(fill="x", padx=10, pady=5)
        
    def _show_logic_content(self):
        """Shows logic puzzle configuration."""
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Logic Puzzle",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        # Puzzle statement
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Logic Problem Statement:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.logic_statement = ctk.CTkTextbox(self.puzzle_content_frame, height=100)
        self.logic_statement.pack(fill="x", padx=10, pady=5)
        
        # Clues
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Clues (one per line):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.logic_clues = ctk.CTkTextbox(self.puzzle_content_frame, height=80)
        self.logic_clues.pack(fill="x", padx=10, pady=5)
        
        # Solution
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Solution:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.logic_solution = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="The logical conclusion"
        )
        self.logic_solution.pack(fill="x", padx=10, pady=5)
        
    def _show_pattern_content(self):
        """Shows pattern puzzle configuration."""
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Pattern Recognition Puzzle",
            font=FONT_PROPERTIES_LABEL
        ).pack(pady=10)
        
        # Pattern type
        pattern_type_frame = ctk.CTkFrame(self.puzzle_content_frame, fg_color="transparent")
        pattern_type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            pattern_type_frame, text="Pattern Type:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.pattern_type = ctk.CTkComboBox(
            pattern_type_frame,
            values=["Visual Grid", "Number Matrix", "Symbol Sequence", "Color Pattern"],
            width=150
        )
        self.pattern_type.set("Visual Grid")
        self.pattern_type.pack(side="left", padx=5)
        
        # Grid size (for visual patterns)
        grid_size_frame = ctk.CTkFrame(self.puzzle_content_frame, fg_color="transparent")
        grid_size_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            grid_size_frame, text="Grid Size:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(side="left", padx=5)
        
        self.grid_width = ctk.CTkEntry(grid_size_frame, placeholder_text="4", width=50)
        self.grid_width.pack(side="left", padx=5)
        
        ctk.CTkLabel(grid_size_frame, text="x").pack(side="left", padx=5)
        
        self.grid_height = ctk.CTkEntry(grid_size_frame, placeholder_text="4", width=50)
        self.grid_height.pack(side="left", padx=5)
        
        # Pattern definition
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Pattern Definition (use symbols/numbers):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.pattern_definition = ctk.CTkTextbox(self.puzzle_content_frame, height=100)
        self.pattern_definition.pack(fill="x", padx=10, pady=5)
        
        # Missing element
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Position of Missing Element (x,y):",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.missing_element = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="2,3"
        )
        self.missing_element.pack(fill="x", padx=10, pady=5)
        
        # Correct answer
        ctk.CTkLabel(
            self.puzzle_content_frame,
            text="Correct Answer:",
            font=FONT_PROPERTIES_ENTRY
        ).pack(anchor="w", padx=10)
        
        self.pattern_answer = ctk.CTkEntry(
            self.puzzle_content_frame,
            placeholder_text="The missing symbol/number"
        )
        self.pattern_answer.pack(fill="x", padx=10, pady=5)
        
    def _auto_encrypt(self):
        """Auto-encrypts text based on selected cipher."""
        original = self.original_text.get("1.0", "end-1c")
        cipher_type = self.cipher_type.get()
        
        if cipher_type == "Caesar":
            # Simple Caesar cipher with shift of 3
            encrypted = ""
            for char in original:
                if char.isalpha():
                    ascii_offset = 65 if char.isupper() else 97
                    encrypted += chr((ord(char) - ascii_offset + 3) % 26 + ascii_offset)
                else:
                    encrypted += char
                    
        elif cipher_type == "Reverse":
            encrypted = original[::-1]
            
        elif cipher_type == "Atbash":
            # A=Z, B=Y, etc.
            encrypted = ""
            for char in original:
                if char.isalpha():
                    if char.isupper():
                        encrypted += chr(90 - (ord(char) - 65))
                    else:
                        encrypted += chr(122 - (ord(char) - 97))
                else:
                    encrypted += char
                    
        else:  # Substitution
            # Simple substitution example
            import random
            alphabet = 'abcdefghijklmnopqrstuvwxyz'
            shuffled = list(alphabet)
            random.shuffle(shuffled)
            sub_map = dict(zip(alphabet, shuffled))
            
            encrypted = ""
            for char in original.lower():
                if char in sub_map:
                    encrypted += sub_map[char]
                else:
                    encrypted += char
                    
        self.encrypted_text.delete("1.0", "end")
        self.encrypted_text.insert("1.0", encrypted)
        
    def save_puzzle_config(self):
        """Saves the current puzzle configuration."""
        puzzle_type = self.puzzle_type_combo.get()
        
        config = {
            'type': puzzle_type,
            'attempts': self.attempts_spinner.get() or "3",
            'hint_cost': self.hint_cost_entry.get() or "10",
            'skip_cost': self.skip_cost_entry.get() or "50",
            'int_bypass': self.int_bypass_entry.get() or "20",
            'rewards': self.rewards_text.get("1.0", "end-1c"),
            'penalties': self.penalties_text.get("1.0", "end-1c")
        }
        
        # Add type-specific configuration
        if puzzle_type == "Riddle":
            config['riddle_text'] = self.riddle_text.get("1.0", "end-1c")
            config['answer'] = self.riddle_answer.get()
            config['hints'] = self.hints_text.get("1.0", "end-1c").split('\n')
            
        elif puzzle_type == "Sequence":
            config['sequence'] = self.sequence_entry.get()
            config['missing_positions'] = self.missing_pos_entry.get()
            config['pattern_hint'] = self.pattern_hint.get()
            
        elif puzzle_type == "Cipher":
            config['cipher_type'] = self.cipher_type.get()
            config['original'] = self.original_text.get("1.0", "end-1c")
            config['encrypted'] = self.encrypted_text.get("1.0", "end-1c")
            
        elif puzzle_type == "Memory":
            config['sequence_length'] = int(self.memory_length_slider.get())
            config['display_time'] = self.display_time_entry.get() or "3000"
            config['elements'] = self.memory_elements.get()
            
        elif puzzle_type == "Logic":
            config['statement'] = self.logic_statement.get("1.0", "end-1c")
            config['clues'] = self.logic_clues.get("1.0", "end-1c").split('\n')
            config['solution'] = self.logic_solution.get()
            
        elif puzzle_type == "Pattern":
            config['pattern_type'] = self.pattern_type.get()
            config['grid_size'] = (self.grid_width.get(), self.grid_height.get())
            config['pattern'] = self.pattern_definition.get("1.0", "end-1c")
            config['missing'] = self.missing_element.get()
            config['answer'] = self.pattern_answer.get()
            
        return config