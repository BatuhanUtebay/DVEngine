# dvge/ui/panels/qte_properties.py

"""Properties panel for Quick Time Event nodes."""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.qte_node import QTENode
from ...features.qte_system import QTEPresets


class QTEPropertiesPanel(ctk.CTkFrame):
    """Properties panel for editing QTE node settings."""

    def __init__(self, parent, on_change_callback=None):
        super().__init__(parent)
        self.on_change_callback = on_change_callback
        self.current_node = None
        self._ignore_changes = False

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        # Title
        title_label = ctk.CTkLabel(
            self, text="QTE Properties", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=(10, 20), padx=20)

        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=400)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.setup_basic_settings()
        self.setup_qte_type_settings()
        self.setup_visual_settings()
        self.setup_outcome_settings()
        self.setup_accessibility_settings()
        self.setup_preset_buttons()

    def setup_basic_settings(self):
        """Setup basic QTE settings."""
        # Basic Settings Frame
        basic_frame = ctk.CTkFrame(self.scroll_frame)
        basic_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(basic_frame, text="Basic Settings",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        # QTE Type
        type_frame = ctk.CTkFrame(basic_frame)
        type_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(type_frame, text="QTE Type:").pack(side="left", padx=5)

        self.qte_type_var = ctk.StringVar(value="sequence")
        self.qte_type_combo = ctk.CTkComboBox(
            type_frame,
            variable=self.qte_type_var,
            values=["sequence", "mash", "hold", "rhythm"],
            command=self._on_qte_type_change
        )
        self.qte_type_combo.pack(side="right", padx=5)

        # Time Limit
        time_frame = ctk.CTkFrame(basic_frame)
        time_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(time_frame, text="Time Limit (seconds):").pack(
            side="left", padx=5)

        self.time_limit_var = ctk.DoubleVar(value=3.0)
        self.time_limit_entry = ctk.CTkEntry(
            time_frame, textvariable=self.time_limit_var, width=100)
        self.time_limit_entry.pack(side="right", padx=5)
        self.time_limit_entry.bind("<KeyRelease>", self._on_change)

        # Difficulty
        diff_frame = ctk.CTkFrame(basic_frame)
        diff_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(diff_frame, text="Difficulty:").pack(side="left", padx=5)

        self.difficulty_var = ctk.StringVar(value="normal")
        self.difficulty_combo = ctk.CTkComboBox(
            diff_frame,
            variable=self.difficulty_var,
            values=["easy", "normal", "hard"],
            command=self._on_change
        )
        self.difficulty_combo.pack(side="right", padx=5)

    def setup_qte_type_settings(self):
        """Setup type-specific QTE settings."""
        # Type-specific Settings Frame
        self.type_specific_frame = ctk.CTkFrame(self.scroll_frame)
        self.type_specific_frame.pack(fill="x", padx=10, pady=5)

        self.type_label = ctk.CTkLabel(
            self.type_specific_frame,
            text="Sequence Settings",
            font=ctk.CTkFont(weight="bold")
        )
        self.type_label.pack(pady=5)

        # Container for type-specific widgets
        self.type_content_frame = ctk.CTkFrame(self.type_specific_frame)
        self.type_content_frame.pack(fill="x", padx=10, pady=5)

        # Initialize with sequence settings
        self._setup_sequence_settings()

    def _setup_sequence_settings(self):
        """Setup sequence-specific settings."""
        self._clear_type_content()
        self.type_label.configure(text="Sequence Settings")

        # Button Sequence
        seq_frame = ctk.CTkFrame(self.type_content_frame)
        seq_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(seq_frame, text="Button Sequence:").pack(
            anchor="w", padx=5)

        # Button sequence editor
        self.sequence_frame = ctk.CTkFrame(seq_frame)
        self.sequence_frame.pack(fill="x", padx=5, pady=5)

        self.sequence_entry = ctk.CTkEntry(
            self.sequence_frame,
            placeholder_text="Enter buttons separated by spaces (e.g., W A S D)"
        )
        self.sequence_entry.pack(
            side="left", fill="x", expand=True, padx=(0, 5))
        self.sequence_entry.bind("<KeyRelease>", self._on_sequence_change)

        add_btn = ctk.CTkButton(
            self.sequence_frame,
            text="Add",
            width=50,
            command=self._add_sequence_button
        )
        add_btn.pack(side="right")

        # Sequence timing
        timing_frame = ctk.CTkFrame(self.type_content_frame)
        timing_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(timing_frame, text="Timing Between Buttons:").pack(
            side="left", padx=5)

        self.sequence_timing_var = ctk.DoubleVar(value=1.0)
        self.sequence_timing_entry = ctk.CTkEntry(
            timing_frame,
            textvariable=self.sequence_timing_var,
            width=100
        )
        self.sequence_timing_entry.pack(side="right", padx=5)
        self.sequence_timing_entry.bind("<KeyRelease>", self._on_change)

        # Advanced sequence options
        self.allow_early_var = ctk.BooleanVar()
        self.allow_early_check = ctk.CTkCheckBox(
            self.type_content_frame,
            text="Allow Early Button Press",
            variable=self.allow_early_var,
            command=self._on_change
        )
        self.allow_early_check.pack(anchor="w", padx=5, pady=2)

        self.exact_timing_var = ctk.BooleanVar()
        self.exact_timing_check = ctk.CTkCheckBox(
            self.type_content_frame,
            text="Require Exact Timing",
            variable=self.exact_timing_var,
            command=self._on_change
        )
        self.exact_timing_check.pack(anchor="w", padx=5, pady=2)

    def _setup_mash_settings(self):
        """Setup button mashing settings."""
        self._clear_type_content()
        self.type_label.configure(text="Button Mashing Settings")

        # Mash Button
        button_frame = ctk.CTkFrame(self.type_content_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(button_frame, text="Button to Mash:").pack(
            side="left", padx=5)

        self.mash_button_var = ctk.StringVar(value="SPACE")
        self.mash_button_combo = ctk.CTkComboBox(
            button_frame,
            variable=self.mash_button_var,
            values=["SPACE", "E", "F", "ENTER", "LEFT_CLICK"],
            command=self._on_change
        )
        self.mash_button_combo.pack(side="right", padx=5)

        # Target Count
        count_frame = ctk.CTkFrame(self.type_content_frame)
        count_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(count_frame, text="Target Presses:").pack(
            side="left", padx=5)

        self.mash_target_var = ctk.IntVar(value=10)
        self.mash_target_entry = ctk.CTkEntry(
            count_frame,
            textvariable=self.mash_target_var,
            width=100
        )
        self.mash_target_entry.pack(side="right", padx=5)
        self.mash_target_entry.bind("<KeyRelease>", self._on_change)

    def _setup_hold_settings(self):
        """Setup button hold settings."""
        self._clear_type_content()
        self.type_label.configure(text="Button Hold Settings")

        # Hold Button
        button_frame = ctk.CTkFrame(self.type_content_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(button_frame, text="Button to Hold:").pack(
            side="left", padx=5)

        self.hold_button_var = ctk.StringVar(value="SPACE")
        self.hold_button_combo = ctk.CTkComboBox(
            button_frame,
            variable=self.hold_button_var,
            values=["SPACE", "E", "F", "ENTER"],
            command=self._on_change
        )
        self.hold_button_combo.pack(side="right", padx=5)

        # Hold Duration
        duration_frame = ctk.CTkFrame(self.type_content_frame)
        duration_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(duration_frame, text="Hold Duration (seconds):").pack(
            side="left", padx=5)

        self.hold_duration_var = ctk.DoubleVar(value=2.0)
        self.hold_duration_entry = ctk.CTkEntry(
            duration_frame,
            textvariable=self.hold_duration_var,
            width=100
        )
        self.hold_duration_entry.pack(side="right", padx=5)
        self.hold_duration_entry.bind("<KeyRelease>", self._on_change)

    def _setup_rhythm_settings(self):
        """Setup rhythm-based settings."""
        self._clear_type_content()
        self.type_label.configure(text="Rhythm Settings")

        # Rhythm Pattern
        pattern_frame = ctk.CTkFrame(self.type_content_frame)
        pattern_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(pattern_frame, text="Rhythm Pattern:").pack(
            anchor="w", padx=5)
        ctk.CTkLabel(
            pattern_frame,
            text="(Beat timings in seconds, separated by spaces)",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=5)

        self.rhythm_pattern_entry = ctk.CTkEntry(
            pattern_frame,
            placeholder_text="e.g., 1.0 0.5 0.5 1.0"
        )
        self.rhythm_pattern_entry.pack(fill="x", padx=5, pady=5)
        self.rhythm_pattern_entry.bind("<KeyRelease>", self._on_change)

        # Timing Tolerance
        tolerance_frame = ctk.CTkFrame(self.type_content_frame)
        tolerance_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(tolerance_frame, text="Timing Tolerance:").pack(
            side="left", padx=5)

        self.rhythm_tolerance_var = ctk.DoubleVar(value=0.2)
        self.rhythm_tolerance_entry = ctk.CTkEntry(
            tolerance_frame,
            textvariable=self.rhythm_tolerance_var,
            width=100
        )
        self.rhythm_tolerance_entry.pack(side="right", padx=5)
        self.rhythm_tolerance_entry.bind("<KeyRelease>", self._on_change)

    def setup_visual_settings(self):
        """Setup visual appearance settings."""
        visual_frame = ctk.CTkFrame(self.scroll_frame)
        visual_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(visual_frame, text="Visual Settings",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        # Visual Options
        self.show_prompts_var = ctk.BooleanVar(value=True)
        self.show_prompts_check = ctk.CTkCheckBox(
            visual_frame,
            text="Show Button Prompts",
            variable=self.show_prompts_var,
            command=self._on_change
        )
        self.show_prompts_check.pack(anchor="w", padx=10, pady=2)

        self.show_progress_var = ctk.BooleanVar(value=True)
        self.show_progress_check = ctk.CTkCheckBox(
            visual_frame,
            text="Show Progress Bar",
            variable=self.show_progress_var,
            command=self._on_change
        )
        self.show_progress_check.pack(anchor="w", padx=10, pady=2)

        self.show_countdown_var = ctk.BooleanVar(value=True)
        self.show_countdown_check = ctk.CTkCheckBox(
            visual_frame,
            text="Show Countdown Timer",
            variable=self.show_countdown_var,
            command=self._on_change
        )
        self.show_countdown_check.pack(anchor="w", padx=10, pady=2)

        # Prompt Style
        style_frame = ctk.CTkFrame(visual_frame)
        style_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(style_frame, text="Prompt Style:").pack(
            side="left", padx=5)

        self.prompt_style_var = ctk.StringVar(value="modern")
        self.prompt_style_combo = ctk.CTkComboBox(
            style_frame,
            variable=self.prompt_style_var,
            values=["modern", "classic", "minimal"],
            command=self._on_change
        )
        self.prompt_style_combo.pack(side="right", padx=5)

    def setup_outcome_settings(self):
        """Setup outcome and threshold settings."""
        outcome_frame = ctk.CTkFrame(self.scroll_frame)
        outcome_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(outcome_frame, text="Outcomes & Thresholds",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        # Add helpful instruction
        instruction_label = ctk.CTkLabel(
            outcome_frame,
            text="Select destination nodes for each QTE outcome:",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        instruction_label.pack(pady=(0, 10), padx=10)

        # Success Node
        success_frame = ctk.CTkFrame(outcome_frame)
        success_frame.pack(fill="x", padx=10, pady=5)
        success_frame.grid_columnconfigure(1, weight=1)

        success_icon_label = ctk.CTkLabel(
            success_frame, text="✅", font=ctk.CTkFont(size=16))
        success_icon_label.grid(row=0, column=0, padx=(5, 0), sticky="w")

        success_text_label = ctk.CTkLabel(
            success_frame, text="Success Node:", font=ctk.CTkFont(weight="bold"))
        success_text_label.grid(row=0, column=1, padx=5, sticky="w")

        self.success_node_combo = ctk.CTkComboBox(
            success_frame,
            values=["", "[End Game]"],
            command=self._on_success_node_change,
            width=200
        )
        self.success_node_combo.grid(row=0, column=2, padx=5, sticky="e")

        # Failure Node
        failure_frame = ctk.CTkFrame(outcome_frame)
        failure_frame.pack(fill="x", padx=10, pady=5)
        failure_frame.grid_columnconfigure(1, weight=1)

        failure_icon_label = ctk.CTkLabel(
            failure_frame, text="❌", font=ctk.CTkFont(size=16))
        failure_icon_label.grid(row=0, column=0, padx=(5, 0), sticky="w")

        failure_text_label = ctk.CTkLabel(
            failure_frame, text="Failure Node:", font=ctk.CTkFont(weight="bold"))
        failure_text_label.grid(row=0, column=1, padx=5, sticky="w")

        self.failure_node_combo = ctk.CTkComboBox(
            failure_frame,
            values=["", "[End Game]"],
            command=self._on_failure_node_change,
            width=200
        )
        self.failure_node_combo.grid(row=0, column=2, padx=5, sticky="e")

        # Partial Success Node
        partial_frame = ctk.CTkFrame(outcome_frame)
        partial_frame.pack(fill="x", padx=10, pady=5)
        partial_frame.grid_columnconfigure(1, weight=1)

        partial_icon_label = ctk.CTkLabel(
            partial_frame, text="⚠️", font=ctk.CTkFont(size=16))
        partial_icon_label.grid(row=0, column=0, padx=(5, 0), sticky="w")

        partial_text_label = ctk.CTkLabel(
            partial_frame, text="Partial Success:", font=ctk.CTkFont(weight="bold"))
        partial_text_label.grid(row=0, column=1, padx=5, sticky="w")

        self.partial_success_node_combo = ctk.CTkComboBox(
            partial_frame,
            values=["", "[End Game]"],
            command=self._on_partial_success_node_change,
            width=200
        )
        self.partial_success_node_combo.grid(
            row=0, column=2, padx=5, sticky="e")

        # Thresholds
        threshold_frame = ctk.CTkFrame(outcome_frame)
        threshold_frame.pack(fill="x", padx=10, pady=5)

        # Success Threshold
        success_thresh_frame = ctk.CTkFrame(threshold_frame)
        success_thresh_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(success_thresh_frame, text="Success Threshold:").pack(
            side="left", padx=5)

        self.success_threshold_var = ctk.DoubleVar(value=0.7)
        self.success_threshold_entry = ctk.CTkEntry(
            success_thresh_frame,
            textvariable=self.success_threshold_var,
            width=100
        )
        self.success_threshold_entry.pack(side="right", padx=5)
        self.success_threshold_entry.bind("<KeyRelease>", self._on_change)

        # Perfect Threshold
        perfect_thresh_frame = ctk.CTkFrame(threshold_frame)
        perfect_thresh_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(perfect_thresh_frame, text="Perfect Threshold:").pack(
            side="left", padx=5)

        self.perfect_threshold_var = ctk.DoubleVar(value=0.95)
        self.perfect_threshold_entry = ctk.CTkEntry(
            perfect_thresh_frame,
            textvariable=self.perfect_threshold_var,
            width=100
        )
        self.perfect_threshold_entry.pack(side="right", padx=5)
        self.perfect_threshold_entry.bind("<KeyRelease>", self._on_change)

    def setup_accessibility_settings(self):
        """Setup accessibility options."""
        access_frame = ctk.CTkFrame(self.scroll_frame)
        access_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(access_frame, text="Accessibility",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        self.auto_complete_var = ctk.BooleanVar()
        self.auto_complete_check = ctk.CTkCheckBox(
            access_frame,
            text="Auto-Complete Mode (Skip QTE)",
            variable=self.auto_complete_var,
            command=self._on_change
        )
        self.auto_complete_check.pack(anchor="w", padx=10, pady=2)

        self.simplified_controls_var = ctk.BooleanVar()
        self.simplified_controls_check = ctk.CTkCheckBox(
            access_frame,
            text="Simplified Controls",
            variable=self.simplified_controls_var,
            command=self._on_change
        )
        self.simplified_controls_check.pack(anchor="w", padx=10, pady=2)

        self.visual_only_var = ctk.BooleanVar()
        self.visual_only_check = ctk.CTkCheckBox(
            access_frame,
            text="Visual Indicators Only",
            variable=self.visual_only_var,
            command=self._on_change
        )
        self.visual_only_check.pack(anchor="w", padx=10, pady=2)

    def setup_preset_buttons(self):
        """Setup preset configuration buttons."""
        preset_frame = ctk.CTkFrame(self.scroll_frame)
        preset_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(preset_frame, text="Quick Presets",
                     font=ctk.CTkFont(weight="bold")).pack(pady=5)

        preset_buttons_frame = ctk.CTkFrame(preset_frame)
        preset_buttons_frame.pack(fill="x", padx=10, pady=5)

        dodge_btn = ctk.CTkButton(
            preset_buttons_frame,
            text="Dodge Sequence",
            command=lambda: self._apply_preset(
                QTEPresets.create_dodge_sequence())
        )
        dodge_btn.pack(side="left", padx=5, expand=True, fill="x")

        mash_btn = ctk.CTkButton(
            preset_buttons_frame,
            text="Button Mash",
            command=lambda: self._apply_preset(QTEPresets.create_button_mash())
        )
        mash_btn.pack(side="left", padx=5, expand=True, fill="x")

        hold_btn = ctk.CTkButton(
            preset_buttons_frame,
            text="Precision Hold",
            command=lambda: self._apply_preset(
                QTEPresets.create_precision_hold())
        )
        hold_btn.pack(side="left", padx=5, expand=True, fill="x")

        rhythm_btn = ctk.CTkButton(
            preset_buttons_frame,
            text="Rhythm",
            command=lambda: self._apply_preset(
                QTEPresets.create_conversation_rhythm())
        )
        rhythm_btn.pack(side="left", padx=5, expand=True, fill="x")

    def _clear_type_content(self):
        """Clear type-specific content frame."""
        for widget in self.type_content_frame.winfo_children():
            widget.destroy()

    def _on_qte_type_change(self, value=None):
        """Handle QTE type change."""
        qte_type = self.qte_type_var.get()

        if qte_type == "sequence":
            self._setup_sequence_settings()
        elif qte_type == "mash":
            self._setup_mash_settings()
        elif qte_type == "hold":
            self._setup_hold_settings()
        elif qte_type == "rhythm":
            self._setup_rhythm_settings()

        self._on_change()

    def _on_sequence_change(self, event=None):
        """Handle sequence entry change."""
        self._on_change()

    def _add_sequence_button(self):
        """Add button to sequence from entry."""
        current_text = self.sequence_entry.get().strip()
        if current_text:
            # Add to sequence if not empty
            self._on_change()

    def _on_success_node_change(self, choice):
        """Handle success node selection change."""
        if self.current_node:
            self.current_node.success_node = choice if choice != "" else ""
            self._trigger_change_callback()

    def _on_failure_node_change(self, choice):
        """Handle failure node selection change."""
        if self.current_node:
            self.current_node.failure_node = choice if choice != "" else ""
            self._trigger_change_callback()

    def _on_partial_success_node_change(self, choice):
        """Handle partial success node selection change."""
        if self.current_node:
            self.current_node.partial_success_node = choice if choice != "" else ""
            self._trigger_change_callback()

    def _trigger_change_callback(self):
        """Trigger the change callback if available."""
        if self.on_change_callback:
            self.on_change_callback()

    def _update_node_dropdowns(self):
        """Update dropdown lists with available nodes."""
        try:
            # Try to get nodes from the app (we need access to the app instance)
            if hasattr(self, '_app_ref') and self._app_ref:
                node_ids = ["", "[End Game]"] + sorted([
                    nid for nid in self._app_ref.nodes.keys()
                    if nid != (self.current_node.id if self.current_node else None)
                ])
            else:
                # Fallback - basic options
                node_ids = ["", "[End Game]"]

            # Update all dropdown values
            self.success_node_combo.configure(values=node_ids)
            self.failure_node_combo.configure(values=node_ids)
            self.partial_success_node_combo.configure(values=node_ids)

        except Exception as e:
            # Fallback if there's any issue
            default_values = ["", "[End Game]"]
            self.success_node_combo.configure(values=default_values)
            self.failure_node_combo.configure(values=default_values)
            self.partial_success_node_combo.configure(values=default_values)

    def set_app_reference(self, app):
        """Set reference to the main application for accessing nodes."""
        self._app_ref = app

    def refresh_node_lists(self):
        """Refresh dropdown lists with current available nodes. Call when nodes are added/removed."""
        if hasattr(self, 'success_node_combo'):  # Check if UI is initialized
            self._update_node_dropdowns()

    def _apply_preset(self, preset_config):
        """Apply a preset configuration."""
        if not self.current_node:
            return

        self._ignore_changes = True
        try:
            # Apply preset values
            for key, value in preset_config.items():
                if hasattr(self.current_node, key):
                    setattr(self.current_node, key, value)

            # Update UI
            self.load_node(self.current_node)

        finally:
            self._ignore_changes = False

        # Trigger change callback
        self._on_change()

    def _on_change(self, event=None):
        """Handle any property change."""
        if self._ignore_changes or not self.current_node:
            return

        # Update node properties from UI
        self._update_node_from_ui()

        # Call change callback
        if self.on_change_callback:
            self.on_change_callback()

    def _update_node_from_ui(self):
        """Update node properties from UI values."""
        if not self.current_node:
            return

        try:
            # Basic settings
            self.current_node.qte_type = self.qte_type_var.get()
            self.current_node.time_limit = self.time_limit_var.get()
            self.current_node.difficulty = self.difficulty_var.get()

            # Visual settings
            self.current_node.show_button_prompts = self.show_prompts_var.get()
            self.current_node.show_progress_bar = self.show_progress_var.get()
            self.current_node.show_countdown = self.show_countdown_var.get()
            self.current_node.prompt_style = self.prompt_style_var.get()

            # Outcome settings are handled by the dropdown callbacks
            # No need to update them here as they're updated immediately
            self.current_node.success_threshold = self.success_threshold_var.get()
            self.current_node.perfect_threshold = self.perfect_threshold_var.get()

            # Accessibility settings
            self.current_node.auto_complete_mode = self.auto_complete_var.get()
            self.current_node.simplified_controls = self.simplified_controls_var.get()
            self.current_node.visual_indicators_only = self.visual_only_var.get()

            # Type-specific settings
            if self.current_node.qte_type == "sequence":
                sequence_text = self.sequence_entry.get().strip()
                if sequence_text:
                    self.current_node.button_sequence = sequence_text.upper().split()
                self.current_node.sequence_timing = self.sequence_timing_var.get()
                self.current_node.allow_early_press = self.allow_early_var.get()
                self.current_node.require_exact_timing = self.exact_timing_var.get()

            elif self.current_node.qte_type == "mash":
                self.current_node.mash_button = self.mash_button_var.get()
                self.current_node.mash_target_count = self.mash_target_var.get()

            elif self.current_node.qte_type == "hold":
                self.current_node.hold_button = self.hold_button_var.get()
                self.current_node.hold_duration = self.hold_duration_var.get()

            elif self.current_node.qte_type == "rhythm":
                pattern_text = self.rhythm_pattern_entry.get().strip()
                if pattern_text:
                    try:
                        pattern = [float(x) for x in pattern_text.split()]
                        self.current_node.rhythm_pattern = pattern
                    except ValueError:
                        pass  # Keep existing pattern if invalid
                self.current_node.rhythm_tolerance = self.rhythm_tolerance_var.get()

        except (ValueError, AttributeError) as e:
            # Handle conversion errors gracefully
            print(f"Error updating QTE node: {e}")

    def load_node(self, node):
        """Load node data into the panel."""
        self.current_node = node
        self._ignore_changes = True

        try:
            # Update dropdowns first to ensure latest node list
            self._update_node_dropdowns()

            # Basic settings
            self.qte_type_var.set(getattr(node, 'qte_type', 'sequence'))
            self.time_limit_var.set(getattr(node, 'time_limit', 3.0))
            self.difficulty_var.set(getattr(node, 'difficulty', 'normal'))

            # Visual settings
            self.show_prompts_var.set(
                getattr(node, 'show_button_prompts', True))
            self.show_progress_var.set(
                getattr(node, 'show_progress_bar', True))
            self.show_countdown_var.set(getattr(node, 'show_countdown', True))
            self.prompt_style_var.set(getattr(node, 'prompt_style', 'modern'))

            # Outcome settings - update combo boxes with available nodes
            self._update_node_dropdowns()

            self.success_node_combo.set(getattr(node, 'success_node', ''))
            self.failure_node_combo.set(getattr(node, 'failure_node', ''))
            self.partial_success_node_combo.set(
                getattr(node, 'partial_success_node', ''))

            self.success_threshold_var.set(
                getattr(node, 'success_threshold', 0.7))
            self.perfect_threshold_var.set(
                getattr(node, 'perfect_threshold', 0.95))

            # Accessibility settings
            self.auto_complete_var.set(
                getattr(node, 'auto_complete_mode', False))
            self.simplified_controls_var.set(
                getattr(node, 'simplified_controls', False))
            self.visual_only_var.set(
                getattr(node, 'visual_indicators_only', False))

            # Update type-specific UI
            self._on_qte_type_change()

            # Load type-specific values
            if node.qte_type == "sequence":
                sequence_str = ' '.join(
                    getattr(node, 'button_sequence', ['SPACE']))
                self.sequence_entry.delete(0, 'end')
                self.sequence_entry.insert(0, sequence_str)
                self.sequence_timing_var.set(
                    getattr(node, 'sequence_timing', 1.0))
                self.allow_early_var.set(
                    getattr(node, 'allow_early_press', False))
                self.exact_timing_var.set(
                    getattr(node, 'require_exact_timing', False))

            elif node.qte_type == "mash":
                self.mash_button_var.set(getattr(node, 'mash_button', 'SPACE'))
                self.mash_target_var.set(
                    getattr(node, 'mash_target_count', 10))

            elif node.qte_type == "hold":
                self.hold_button_var.set(getattr(node, 'hold_button', 'SPACE'))
                self.hold_duration_var.set(getattr(node, 'hold_duration', 2.0))

            elif node.qte_type == "rhythm":
                pattern = getattr(node, 'rhythm_pattern', [1.0, 0.5, 0.5, 1.0])
                pattern_str = ' '.join(str(x) for x in pattern)
                self.rhythm_pattern_entry.delete(0, 'end')
                self.rhythm_pattern_entry.insert(0, pattern_str)
                self.rhythm_tolerance_var.set(
                    getattr(node, 'rhythm_tolerance', 0.2))

        finally:
            self._ignore_changes = False

    def clear(self):
        """Clear the panel."""
        self.current_node = None
        # Reset all UI elements to defaults
        self._ignore_changes = True
        try:
            self.qte_type_var.set("sequence")
            self.time_limit_var.set(3.0)
            self.difficulty_var.set("normal")
            self.show_prompts_var.set(True)
            self.show_progress_var.set(True)
            self.show_countdown_var.set(True)
            self.prompt_style_var.set("modern")

            # Reset combo boxes
            self.success_node_combo.set("")
            self.failure_node_combo.set("")
            self.partial_success_node_combo.set("")

            self.success_threshold_var.set(0.7)
            self.perfect_threshold_var.set(0.95)

            self.auto_complete_var.set(False)
            self.simplified_controls_var.set(False)
            self.visual_only_var.set(False)

            self._on_qte_type_change()
        finally:
            self._ignore_changes = False
