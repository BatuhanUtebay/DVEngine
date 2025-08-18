# dvge/ui/windows/advanced_media_window.py

"""Advanced Media Manager Window for DVGE - Professional multimedia system."""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import json
from typing import TYPE_CHECKING, Optional, Dict, List, Any
from PIL import Image, ImageTk

if TYPE_CHECKING:
    from ...core.application import DVGApp

# Try to import advanced media system
try:
    from ...features.media_system import MediaLibrary, MediaAsset, MediaType, AnimationType, EasingType
    ADVANCED_MEDIA_AVAILABLE = True
except ImportError:
    ADVANCED_MEDIA_AVAILABLE = False
    # Create dummy classes for fallback
    class MediaType:
        IMAGE = "image"
        VIDEO = "video" 
        AUDIO = "audio"
        MUSIC = "music"


class AdvancedMediaWindow(ctk.CTkToplevel):
    """Advanced professional media manager with full multimedia capabilities."""

    def __init__(self, parent, app_ref=None):
        super().__init__(parent)
        
        self.app_ref = app_ref
        self.current_node = None
        self.selected_asset_id = None
        self.media_assets = {}  # Local asset storage
        self.asset_previews = {}  # Thumbnail cache
        
        # Window setup - much larger for advanced features
        self.title("Advanced Media Manager - DVGE Pro")
        self.geometry("1400x900")
        self.transient(parent)
        
        # Load current node
        if app_ref and hasattr(app_ref, 'active_node_id') and app_ref.active_node_id:
            self.current_node = app_ref.nodes.get(app_ref.active_node_id)
        
        # Initialize media library
        self.media_library = None
        if app_ref and hasattr(app_ref, 'media_library'):
            self.media_library = app_ref.media_library
        elif ADVANCED_MEDIA_AVAILABLE:
            self.media_library = MediaLibrary()
        
        self.create_advanced_ui()
        self.load_node_data()

    def create_advanced_ui(self):
        """Create the advanced media manager UI."""
        
        # Header with advanced controls
        self.create_header()
        
        # Main content - tabbed interface
        self.create_tabbed_interface()
        
        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create advanced header with toolbar."""
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Left side - Title and node info
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)
        
        title_label = ctk.CTkLabel(
            left_frame,
            text="Advanced Media Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.node_info_label = ctk.CTkLabel(
            left_frame,
            text="No node selected",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.node_info_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Right side - Action buttons
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=15)
        
        # Import buttons
        import_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        import_frame.pack(side="left", padx=10)
        
        ctk.CTkButton(
            import_frame,
            text="Import Assets",
            command=self.import_multiple_assets,
            width=120,
            fg_color="#4A90E2",
            hover_color="#357ABD"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            import_frame,
            text="Advanced Import",
            command=self.advanced_import,
            width=120,
            fg_color="#7B68EE",
            hover_color="#6A5ACD"
        ).pack(side="left", padx=5)
        
        # Save/Close buttons
        action_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        action_frame.pack(side="left", padx=10)
        
        ctk.CTkButton(
            action_frame,
            text="Apply & Preview",
            command=self.apply_and_preview,
            width=120,
            fg_color="#2E8B57",
            hover_color="#228B22"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Close",
            command=self.destroy,
            width=80,
            fg_color="gray"
        ).pack(side="left", padx=5)

    def create_tabbed_interface(self):
        """Create the main tabbed interface."""
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab_view.add("Asset Library")
        self.tab_view.add("Timeline & Animation")
        self.tab_view.add("Effects & Filters")
        self.tab_view.add("Audio Mixer")
        self.tab_view.add("Export & Settings")
        
        # Setup each tab
        self.setup_asset_library_tab()
        self.setup_timeline_tab()
        self.setup_effects_tab()
        self.setup_audio_tab()
        self.setup_export_tab()

    def setup_asset_library_tab(self):
        """Setup the asset library tab with thumbnails and management."""
        tab = self.tab_view.tab("Asset Library")
        
        # Main layout - 3 columns
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left column - Asset browser
        browser_frame = ctk.CTkFrame(main_frame)
        browser_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Asset browser header
        browser_header = ctk.CTkFrame(browser_frame)
        browser_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            browser_header,
            text="Media Assets",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        # Filter dropdown
        self.asset_filter_var = ctk.StringVar(value="All")
        filter_combo = ctk.CTkComboBox(
            browser_header,
            variable=self.asset_filter_var,
            values=["All", "Images", "Videos", "Audio", "Music"],
            command=self.filter_assets,
            width=100
        )
        filter_combo.pack(side="right", padx=10)
        
        # Asset grid/list
        self.asset_list_frame = ctk.CTkScrollableFrame(browser_frame)
        self.asset_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Middle column - Asset preview
        preview_frame = ctk.CTkFrame(main_frame, width=300)
        preview_frame.pack(side="left", fill="y", padx=5)
        preview_frame.pack_propagate(False)
        
        # Preview header
        ctk.CTkLabel(
            preview_frame,
            text="Asset Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Preview area
        self.preview_frame_inner = ctk.CTkFrame(preview_frame, height=200)
        self.preview_frame_inner.pack(fill="x", padx=15, pady=10)
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame_inner,
            text="Select an asset to preview",
            height=150,
            text_color="#666666"
        )
        self.preview_label.pack(expand=True, pady=30)
        
        # Asset details
        details_frame = ctk.CTkFrame(preview_frame)
        details_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            details_frame,
            text="Asset Details",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.asset_details_text = ctk.CTkTextbox(details_frame, height=150)
        self.asset_details_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right column - Properties and actions
        properties_frame = ctk.CTkFrame(main_frame, width=280)
        properties_frame.pack(side="right", fill="y", padx=(5, 0))
        properties_frame.pack_propagate(False)
        
        # Properties header
        ctk.CTkLabel(
            properties_frame,
            text="Asset Properties",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Transform properties
        self.setup_transform_properties(properties_frame)
        
        # Asset actions
        self.setup_asset_actions(properties_frame)

    def setup_transform_properties(self, parent):
        """Setup transform property controls."""
        transform_frame = ctk.CTkFrame(parent)
        transform_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            transform_frame,
            text="Transform",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        # Position
        pos_frame = ctk.CTkFrame(transform_frame)
        pos_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(pos_frame, text="Position:", width=70).pack(side="left", padx=5)
        self.x_var = ctk.DoubleVar(value=0)
        ctk.CTkEntry(pos_frame, textvariable=self.x_var, width=50).pack(side="left", padx=2)
        ctk.CTkLabel(pos_frame, text="x", width=15).pack(side="left")
        self.y_var = ctk.DoubleVar(value=0)
        ctk.CTkEntry(pos_frame, textvariable=self.y_var, width=50).pack(side="left", padx=2)
        ctk.CTkLabel(pos_frame, text="y").pack(side="left")
        
        # Size
        size_frame = ctk.CTkFrame(transform_frame)
        size_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(size_frame, text="Size:", width=70).pack(side="left", padx=5)
        self.width_var = ctk.DoubleVar(value=100)
        ctk.CTkEntry(size_frame, textvariable=self.width_var, width=50).pack(side="left", padx=2)
        ctk.CTkLabel(size_frame, text="w", width=15).pack(side="left")
        self.height_var = ctk.DoubleVar(value=100)
        ctk.CTkEntry(size_frame, textvariable=self.height_var, width=50).pack(side="left", padx=2)
        ctk.CTkLabel(size_frame, text="h").pack(side="left")
        
        # Rotation and Opacity
        rot_frame = ctk.CTkFrame(transform_frame)
        rot_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(rot_frame, text="Rotation:", width=70).pack(side="left", padx=5)
        self.rotation_var = ctk.DoubleVar(value=0)
        ctk.CTkEntry(rot_frame, textvariable=self.rotation_var, width=50).pack(side="left", padx=2)
        
        ctk.CTkLabel(rot_frame, text="Opacity:", width=60).pack(side="left", padx=(10, 5))
        self.opacity_var = ctk.DoubleVar(value=1.0)
        ctk.CTkEntry(rot_frame, textvariable=self.opacity_var, width=50).pack(side="left", padx=2)

    def setup_asset_actions(self, parent):
        """Setup asset action buttons."""
        actions_frame = ctk.CTkFrame(parent)
        actions_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="Actions",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        # Action buttons
        ctk.CTkButton(
            actions_frame,
            text="Add to Node",
            command=self.add_selected_to_node,
            width=200
        ).pack(pady=5, padx=10)
        
        ctk.CTkButton(
            actions_frame,
            text="Duplicate Asset",
            command=self.duplicate_asset,
            width=200
        ).pack(pady=5, padx=10)
        
        ctk.CTkButton(
            actions_frame,
            text="Delete Asset",
            command=self.delete_asset,
            width=200,
            fg_color="red",
            hover_color="darkred"
        ).pack(pady=5, padx=10)
        
        # Layer controls
        layer_frame = ctk.CTkFrame(actions_frame)
        layer_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(layer_frame, text="Layer Order:").pack(pady=5)
        
        layer_buttons = ctk.CTkFrame(layer_frame)
        layer_buttons.pack()
        
        ctk.CTkButton(
            layer_buttons,
            text="Front",
            command=self.bring_to_front,
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            layer_buttons,
            text="Forward",
            command=self.bring_forward,
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            layer_buttons,
            text="Back",
            command=self.send_backward,
            width=60
        ).pack(side="left", padx=2)

    def setup_timeline_tab(self):
        """Setup the timeline and animation tab."""
        tab = self.tab_view.tab("Timeline & Animation")
        
        # Timeline header
        timeline_header = ctk.CTkFrame(tab)
        timeline_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            timeline_header,
            text="Animation Timeline",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=20)
        
        # Timeline controls
        controls_frame = ctk.CTkFrame(timeline_header)
        controls_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            controls_frame,
            text="Play",
            command=self.play_timeline,
            width=80
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="Stop",
            command=self.stop_timeline,
            width=80
        ).pack(side="left", padx=5)
        
        # Timeline canvas
        timeline_frame = ctk.CTkFrame(tab, height=300)
        timeline_frame.pack(fill="x", padx=10, pady=10)
        timeline_frame.pack_propagate(False)
        
        # Create timeline canvas
        self.timeline_canvas = tk.Canvas(
            timeline_frame,
            bg="#2b2b2b",
            height=280,
            highlightthickness=0
        )
        self.timeline_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Draw initial timeline
        self.after(100, self.draw_initial_timeline)
        
        # Animation controls
        anim_controls = ctk.CTkFrame(tab)
        anim_controls.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Animation types
        anim_left = ctk.CTkFrame(anim_controls)
        anim_left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(
            anim_left,
            text="Animation Presets",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Animation preset buttons
        presets = [
            ("Fade In", self.add_fade_in),
            ("Slide In", self.add_slide_in),
            ("Scale Up", self.add_scale_up),
            ("Rotate", self.add_rotation),
            ("Bounce", self.add_bounce),
            ("Elastic", self.add_elastic)
        ]
        
        for i, (name, command) in enumerate(presets):
            if i % 2 == 0:
                row_frame = ctk.CTkFrame(anim_left)
                row_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkButton(
                row_frame,
                text=name,
                command=command,
                width=120
            ).pack(side="left" if i % 2 == 0 else "right", padx=5)
        
        # Right side - Keyframe editor
        anim_right = ctk.CTkFrame(anim_controls)
        anim_right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(
            anim_right,
            text="Keyframe Editor",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Keyframe properties
        kf_props = ctk.CTkFrame(anim_right)
        kf_props.pack(fill="x", padx=15, pady=10)
        
        # Duration
        dur_frame = ctk.CTkFrame(kf_props)
        dur_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(dur_frame, text="Duration (s):").pack(side="left", padx=10)
        self.anim_duration_var = ctk.DoubleVar(value=1.0)
        ctk.CTkEntry(dur_frame, textvariable=self.anim_duration_var, width=100).pack(side="right", padx=10)
        
        # Easing
        ease_frame = ctk.CTkFrame(kf_props)
        ease_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ease_frame, text="Easing:").pack(side="left", padx=10)
        self.easing_var = ctk.StringVar(value="ease-in-out")
        ctk.CTkComboBox(
            ease_frame,
            variable=self.easing_var,
            values=["linear", "ease-in", "ease-out", "ease-in-out", "bounce", "elastic"],
            width=120
        ).pack(side="right", padx=10)

    def setup_effects_tab(self):
        """Setup the effects and filters tab."""
        tab = self.tab_view.tab("Effects & Filters")
        
        # Effects header
        effects_header = ctk.CTkFrame(tab)
        effects_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            effects_header,
            text="Visual Effects & Filters",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=20)
        
        # Main effects area
        effects_main = ctk.CTkFrame(tab)
        effects_main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Effect categories
        effects_left = ctk.CTkFrame(effects_main)
        effects_left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Color effects
        color_frame = ctk.CTkFrame(effects_left)
        color_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            color_frame,
            text="Color Effects",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        color_effects = ctk.CTkFrame(color_frame)
        color_effects.pack(fill="x", padx=10, pady=5)
        
        effects_row1 = ctk.CTkFrame(color_effects)
        effects_row1.pack(fill="x", pady=2)
        
        ctk.CTkButton(effects_row1, text="Brightness", command=self.add_brightness_effect, width=100).pack(side="left", padx=5)
        ctk.CTkButton(effects_row1, text="Contrast", command=self.add_contrast_effect, width=100).pack(side="left", padx=5)
        ctk.CTkButton(effects_row1, text="Saturation", command=self.add_saturation_effect, width=100).pack(side="left", padx=5)
        
        effects_row2 = ctk.CTkFrame(color_effects)
        effects_row2.pack(fill="x", pady=2)
        
        ctk.CTkButton(effects_row2, text="Hue Rotate", command=self.add_hue_rotate_effect, width=100).pack(side="left", padx=5)
        ctk.CTkButton(effects_row2, text="Sepia", command=self.add_sepia_effect, width=100).pack(side="left", padx=5)
        ctk.CTkButton(effects_row2, text="Grayscale", command=self.add_grayscale_effect, width=100).pack(side="left", padx=5)
        
        # Filter effects
        filter_frame = ctk.CTkFrame(effects_left)
        filter_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filter Effects",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        filter_effects = ctk.CTkFrame(filter_frame)
        filter_effects.pack(fill="x", padx=10, pady=5)
        
        filter_row1 = ctk.CTkFrame(filter_effects)
        filter_row1.pack(fill="x", pady=2)
        
        ctk.CTkButton(filter_row1, text="Blur", command=self.add_blur_effect, width=100).pack(side="left", padx=5)
        ctk.CTkButton(filter_row1, text="Drop Shadow", command=self.add_shadow_effect, width=100).pack(side="left", padx=5)
        ctk.CTkButton(filter_row1, text="Glow", command=self.add_glow_effect, width=100).pack(side="left", padx=5)
        
        # Right side - Effect properties
        effects_right = ctk.CTkFrame(effects_main)
        effects_right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(
            effects_right,
            text="Effect Properties",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Effect strength slider
        strength_frame = ctk.CTkFrame(effects_right)
        strength_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(strength_frame, text="Effect Strength").pack(pady=5)
        self.effect_strength_var = ctk.DoubleVar(value=1.0)
        self.effect_strength_slider = ctk.CTkSlider(
            strength_frame,
            from_=0.0,
            to=2.0,
            variable=self.effect_strength_var,
            command=self.update_effect_strength
        )
        self.effect_strength_slider.pack(fill="x", padx=15, pady=5)
        
        # Applied effects list
        effects_list_frame = ctk.CTkFrame(effects_right)
        effects_list_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            effects_list_frame,
            text="Applied Effects",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        self.effects_listbox = tk.Listbox(
            effects_list_frame,
            height=8,
            selectmode=tk.SINGLE,
            font=("Arial", 10)
        )
        self.effects_listbox.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_audio_tab(self):
        """Setup the audio mixer tab."""
        tab = self.tab_view.tab("Audio Mixer")
        
        # Audio header
        audio_header = ctk.CTkFrame(tab)
        audio_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            audio_header,
            text="Audio Mixer & Controls",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=20)
        
        # Main audio area
        audio_main = ctk.CTkFrame(tab)
        audio_main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Audio channels
        channels_frame = ctk.CTkFrame(audio_main)
        channels_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Background Music Channel
        self.create_audio_channel(channels_frame, "Background Music", "music")
        
        # Sound Effects Channel
        self.create_audio_channel(channels_frame, "Sound Effects", "audio")
        
        # Voice/Narration Channel
        self.create_audio_channel(channels_frame, "Voice/Narration", "voice")

    def create_audio_channel(self, parent, title, channel_type):
        """Create an audio channel with controls."""
        channel_frame = ctk.CTkFrame(parent)
        channel_frame.pack(fill="x", padx=10, pady=10)
        
        # Channel header
        header = ctk.CTkFrame(channel_frame)
        header.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Channel controls
        controls = ctk.CTkFrame(header)
        controls.pack(side="right")
        
        # Play/Stop buttons
        ctk.CTkButton(controls, text="Play", width=60).pack(side="left", padx=2)
        ctk.CTkButton(controls, text="Stop", width=60).pack(side="left", padx=2)
        
        # Channel content
        content = ctk.CTkFrame(channel_frame)
        content.pack(fill="x", padx=15, pady=10)
        
        # File selection
        file_frame = ctk.CTkFrame(content)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        file_var = ctk.StringVar()
        file_entry = ctk.CTkEntry(
            file_frame,
            textvariable=file_var,
            placeholder_text=f"Select {title.lower()} file..."
        )
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            file_frame,
            text="Browse",
            command=lambda: self.browse_audio_file(file_var, title),
            width=80
        ).pack(side="right")
        
        # Volume and controls
        vol_frame = ctk.CTkFrame(content)
        vol_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(vol_frame, text="Volume:", width=60).pack(side="left", padx=5)
        vol_var = ctk.DoubleVar(value=1.0)
        vol_slider = ctk.CTkSlider(vol_frame, from_=0.0, to=1.0, variable=vol_var)
        vol_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        vol_label = ctk.CTkLabel(vol_frame, text="100%", width=50)
        vol_label.pack(side="left", padx=5)
        
        # Update volume label
        vol_slider.configure(command=lambda v: vol_label.configure(text=f"{int(float(v)*100)}%"))
        
        # Audio options
        options_frame = ctk.CTkFrame(content)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        loop_var = ctk.BooleanVar()
        ctk.CTkCheckBox(options_frame, text="Loop", variable=loop_var).pack(side="left", padx=10)
        
        autoplay_var = ctk.BooleanVar()
        ctk.CTkCheckBox(options_frame, text="Autoplay", variable=autoplay_var).pack(side="left", padx=10)
        
        fade_var = ctk.BooleanVar()
        ctk.CTkCheckBox(options_frame, text="Fade In/Out", variable=fade_var).pack(side="left", padx=10)

    def setup_export_tab(self):
        """Setup the export and settings tab."""
        tab = self.tab_view.tab("Export & Settings")
        
        # Export header
        export_header = ctk.CTkFrame(tab)
        export_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            export_header,
            text="Export & Project Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=20)
        
        # Main export area
        export_main = ctk.CTkFrame(tab)
        export_main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Export options
        export_left = ctk.CTkFrame(export_main)
        export_left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Export formats
        formats_frame = ctk.CTkFrame(export_left)
        formats_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            formats_frame,
            text="Export Formats",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        export_buttons = ctk.CTkFrame(formats_frame)
        export_buttons.pack(pady=10)
        
        ctk.CTkButton(
            export_buttons,
            text="Export HTML Game",
            command=self.export_html_game,
            width=150,
            fg_color="#2E8B57"
        ).pack(pady=5)
        
        ctk.CTkButton(
            export_buttons,
            text="Export Media Pack",
            command=self.export_media_pack,
            width=150,
            fg_color="#4A90E2"
        ).pack(pady=5)
        
        ctk.CTkButton(
            export_buttons,
            text="Export Asset Library",
            command=self.export_asset_library,
            width=150,
            fg_color="#7B68EE"
        ).pack(pady=5)
        
        # Right side - Settings
        settings_right = ctk.CTkFrame(export_main)
        settings_right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Quality settings
        quality_frame = ctk.CTkFrame(settings_right)
        quality_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            quality_frame,
            text="Quality Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Image quality
        img_quality_frame = ctk.CTkFrame(quality_frame)
        img_quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(img_quality_frame, text="Image Quality:").pack(side="left", padx=5)
        self.img_quality_var = ctk.StringVar(value="High")
        ctk.CTkComboBox(
            img_quality_frame,
            variable=self.img_quality_var,
            values=["Low", "Medium", "High", "Ultra"],
            width=100
        ).pack(side="right", padx=5)
        
        # Audio quality
        audio_quality_frame = ctk.CTkFrame(quality_frame)
        audio_quality_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(audio_quality_frame, text="Audio Quality:").pack(side="left", padx=5)
        self.audio_quality_var = ctk.StringVar(value="High")
        ctk.CTkComboBox(
            audio_quality_frame,
            variable=self.audio_quality_var,
            values=["Low", "Medium", "High", "Lossless"],
            width=100
        ).pack(side="right", padx=5)

    def create_status_bar(self):
        """Create status bar at bottom."""
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready - Advanced Media Manager loaded",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=15, pady=5)
        
        # Asset count
        self.asset_count_label = ctk.CTkLabel(
            self.status_frame,
            text="0 assets loaded",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.asset_count_label.pack(side="right", padx=15, pady=5)

    # Core functionality methods
    def load_node_data(self):
        """Load data from current node."""
        if self.current_node:
            self.node_info_label.configure(
                text=f"Editing media for node: {self.current_node.id}"
            )
            self.status_label.configure(text=f"Loaded node: {self.current_node.id}")
            
            # Load media assets if available
            if hasattr(self.current_node, 'media_assets'):
                self.refresh_asset_library()
        else:
            self.node_info_label.configure(text="No node selected")
            self.status_label.configure(text="No node selected")

    def refresh_asset_library(self):
        """Refresh the asset library display."""
        # Clear current display
        for widget in self.asset_list_frame.winfo_children():
            widget.destroy()
        
        # Show message if no assets
        if not self.media_assets:
            no_assets_label = ctk.CTkLabel(
                self.asset_list_frame,
                text="No media assets loaded\nClick 'Import Assets' to get started",
                font=ctk.CTkFont(size=12),
                text_color="#666666"
            )
            no_assets_label.pack(pady=50)
        
        # Update status
        count = len(self.media_assets)
        self.asset_count_label.configure(text=f"{count} assets loaded")

    # Import and file management
    def import_multiple_assets(self):
        """Import multiple assets at once."""
        filetypes = [
            ("All Supported", "*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.webm *.ogg *.avi *.mov *.mp3 *.wav *.m4a"),
            ("Images", "*.png *.jpg *.jpeg *.gif *.webp"),
            ("Videos", "*.mp4 *.webm *.ogg *.avi *.mov"),
            ("Audio", "*.mp3 *.wav *.ogg *.m4a *.aac"),
            ("All files", "*.*")
        ]
        
        filepaths = filedialog.askopenfilenames(
            title="Import Media Assets",
            filetypes=filetypes,
            parent=self
        )
        
        if filepaths:
            imported_count = 0
            for filepath in filepaths:
                if self.import_single_asset(filepath):
                    imported_count += 1
            
            self.refresh_asset_library()
            self.status_label.configure(text=f"Imported {imported_count} assets")
            
            messagebox.showinfo(
                "Import Complete",
                f"Successfully imported {imported_count} of {len(filepaths)} assets"
            )

    def import_single_asset(self, filepath):
        """Import a single asset."""
        if not os.path.exists(filepath):
            return False
        
        # Generate unique ID
        asset_id = f"asset_{len(self.media_assets) + 1}"
        
        # Determine type
        ext = os.path.splitext(filepath)[1].lower()
        if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
            asset_type = MediaType.IMAGE
        elif ext in ['.mp4', '.webm', '.ogg', '.avi', '.mov']:
            asset_type = MediaType.VIDEO
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            asset_type = MediaType.AUDIO
        else:
            return False
        
        # Create asset data
        asset_data = {
            'id': asset_id,
            'name': os.path.basename(filepath),
            'path': filepath,
            'type': asset_type,
            'properties': {
                'x': 0, 'y': 0, 'width': 100, 'height': 100,
                'rotation': 0, 'opacity': 1.0, 'z_index': 0
            },
            'animations': [],
            'effects': []
        }
        
        self.media_assets[asset_id] = asset_data
        return True

    def advanced_import(self):
        """Show advanced import options."""
        messagebox.showinfo(
            "Advanced Import",
            "Advanced import features:\n\n" +
            "• Batch processing\n" +
            "• Auto-optimization\n" +
            "• Format conversion\n" +
            "• Metadata extraction\n\n" +
            "Coming in next update!"
        )

    # Core functionality methods
    def filter_assets(self, filter_type):
        """Filter assets by type."""
        self.status_label.configure(text=f"Filtering by: {filter_type}")
        
        # Clear current display
        for widget in self.asset_list_frame.winfo_children():
            widget.destroy()
        
        # Filter assets based on type
        filtered_assets = {}
        if filter_type == "All":
            filtered_assets = self.media_assets
        else:
            type_mapping = {
                "Images": MediaType.IMAGE,
                "Videos": MediaType.VIDEO, 
                "Audio": MediaType.AUDIO,
                "Music": MediaType.AUDIO  # Music is also audio type
            }
            target_type = type_mapping.get(filter_type)
            if target_type:
                filtered_assets = {k: v for k, v in self.media_assets.items() 
                                 if v['type'] == target_type}
        
        # Display filtered assets
        self.display_assets(filtered_assets)
    
    def display_assets(self, assets_dict):
        """Display assets in the asset library."""
        if not assets_dict:
            no_assets_label = ctk.CTkLabel(
                self.asset_list_frame,
                text="No assets match the current filter\nTry changing the filter or import new assets",
                font=ctk.CTkFont(size=12),
                text_color="#666666"
            )
            no_assets_label.pack(pady=50)
            return
        
        # Create grid of asset items
        current_row_frame = None
        items_per_row = 3
        item_count = 0
        
        for asset_id, asset_data in assets_dict.items():
            if item_count % items_per_row == 0:
                current_row_frame = ctk.CTkFrame(self.asset_list_frame, fg_color="transparent")
                current_row_frame.pack(fill="x", pady=5)
            
            self.create_asset_item(current_row_frame, asset_id, asset_data)
            item_count += 1
    
    def create_asset_item(self, parent, asset_id, asset_data):
        """Create an individual asset item widget."""
        item_frame = ctk.CTkFrame(parent, width=120, height=100)
        item_frame.pack(side="left", padx=5, pady=5)
        item_frame.pack_propagate(False)
        
        # Asset type indicator
        type_color = {
            MediaType.IMAGE: "#4CAF50",
            MediaType.VIDEO: "#2196F3",
            MediaType.AUDIO: "#FF9800"
        }
        
        # Thumbnail placeholder
        thumb_label = ctk.CTkLabel(
            item_frame,
            text=asset_data['type'].upper()[:3] if hasattr(asset_data['type'], 'upper') else "AST",
            width=80,
            height=60,
            fg_color=type_color.get(asset_data['type'], "#666666"),
            text_color="white",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        thumb_label.pack(pady=(5, 2))
        
        # Asset name (truncated)
        name_text = asset_data['name']
        if len(name_text) > 15:
            name_text = name_text[:12] + "..."
        
        name_label = ctk.CTkLabel(
            item_frame,
            text=name_text,
            font=ctk.CTkFont(size=9),
            height=20
        )
        name_label.pack()
        
        # Bind click event
        def select_this_asset(event=None):
            self.select_asset(asset_id, asset_data)
        
        item_frame.bind("<Button-1>", select_this_asset)
        thumb_label.bind("<Button-1>", select_this_asset)
        name_label.bind("<Button-1>", select_this_asset)
    
    def select_asset(self, asset_id, asset_data):
        """Select an asset and update the preview."""
        self.selected_asset_id = asset_id
        
        # Update preview
        self.preview_label.configure(text=f"Previewing: {asset_data['name']}")
        
        # Update details
        self.asset_details_text.delete(1.0, tk.END)
        details = f"Name: {asset_data['name']}\n"
        details += f"Type: {asset_data['type']}\n"
        details += f"Path: {asset_data['path']}\n"
        details += f"Position: ({asset_data['properties']['x']}, {asset_data['properties']['y']})\n"
        details += f"Size: {asset_data['properties']['width']} x {asset_data['properties']['height']}\n"
        details += f"Rotation: {asset_data['properties']['rotation']}°\n"
        details += f"Opacity: {asset_data['properties']['opacity']}\n"
        details += f"Z-Index: {asset_data['properties']['z_index']}\n"
        details += f"Animations: {len(asset_data['animations'])}\n"
        details += f"Effects: {len(asset_data['effects'])}"
        
        self.asset_details_text.insert(1.0, details)
        
        # Update transform properties
        self.x_var.set(asset_data['properties']['x'])
        self.y_var.set(asset_data['properties']['y'])
        self.width_var.set(asset_data['properties']['width'])
        self.height_var.set(asset_data['properties']['height'])
        self.rotation_var.set(asset_data['properties']['rotation'])
        self.opacity_var.set(asset_data['properties']['opacity'])
        
        self.status_label.configure(text=f"Selected: {asset_data['name']}")

    def add_selected_to_node(self):
        """Add selected asset to current node."""
        if not self.selected_asset_id or not self.current_node:
            messagebox.showwarning("Selection Required", "Please select an asset and ensure a node is active.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if not asset:
            return
        
        # Apply asset to node based on type
        if asset['type'] == MediaType.IMAGE:
            self.current_node.backgroundImage = asset['path']
        elif asset['type'] == MediaType.AUDIO:
            if 'music' in asset['name'].lower() or 'bgm' in asset['name'].lower():
                self.current_node.music = asset['path']
            else:
                self.current_node.audio = asset['path']
        
        # Save state if state manager is available
        if self.app_ref and hasattr(self.app_ref, 'state_manager'):
            self.app_ref.state_manager.save_state(f"Added {asset['name']} to node")
        
        self.status_label.configure(text=f"Added {asset['name']} to node {self.current_node.id}")
        messagebox.showinfo("Success", f"Added {asset['name']} to current node!")

    def duplicate_asset(self):
        """Duplicate selected asset."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset to duplicate.")
            return
        
        original_asset = self.media_assets.get(self.selected_asset_id)
        if not original_asset:
            return
        
        # Create duplicate with new ID
        new_id = f"asset_{len(self.media_assets) + 1}"
        duplicate_asset = original_asset.copy()
        duplicate_asset['id'] = new_id
        duplicate_asset['name'] = f"{original_asset['name']} (Copy)"
        
        # Deep copy nested dictionaries
        duplicate_asset['properties'] = original_asset['properties'].copy()
        duplicate_asset['animations'] = original_asset['animations'].copy()
        duplicate_asset['effects'] = original_asset['effects'].copy()
        
        self.media_assets[new_id] = duplicate_asset
        self.refresh_asset_library()
        self.status_label.configure(text=f"Duplicated {original_asset['name']}")
        messagebox.showinfo("Success", "Asset duplicated successfully!")

    def delete_asset(self):
        """Delete selected asset."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset to delete.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if not asset:
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Delete asset '{asset['name']}'?\n\nThis action cannot be undone."):
            del self.media_assets[self.selected_asset_id]
            self.selected_asset_id = None
            
            # Clear preview
            self.preview_label.configure(text="Select an asset to preview")
            self.asset_details_text.delete(1.0, tk.END)
            
            self.refresh_asset_library()
            self.status_label.configure(text=f"Deleted {asset['name']}")
            messagebox.showinfo("Success", "Asset deleted successfully!")

    def bring_to_front(self):
        """Bring asset to front layer."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            # Find highest z_index
            max_z = max((a['properties'].get('z_index', 0) for a in self.media_assets.values()), default=0)
            asset['properties']['z_index'] = max_z + 1
            self.status_label.configure(text=f"Brought {asset['name']} to front")

    def bring_forward(self):
        """Bring asset forward one layer."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            current_z = asset['properties'].get('z_index', 0)
            asset['properties']['z_index'] = current_z + 1
            self.status_label.configure(text=f"Moved {asset['name']} forward")

    def send_backward(self):
        """Send asset back one layer."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            current_z = asset['properties'].get('z_index', 0)
            asset['properties']['z_index'] = max(0, current_z - 1)
            self.status_label.configure(text=f"Moved {asset['name']} backward")

    def play_timeline(self):
        """Play timeline animation."""
        self.status_label.configure(text="Playing timeline animation...")
        
        # Draw timeline with playhead moving
        self.timeline_canvas.delete("playhead")
        
        # Simple playhead animation simulation
        def animate_playhead(x=0):
            if x < 400:  # Timeline width
                self.timeline_canvas.delete("playhead")
                self.timeline_canvas.create_line(
                    x, 0, x, 280, 
                    fill="#FF6B35", 
                    width=2, 
                    tags="playhead"
                )
                self.after(50, lambda: animate_playhead(x + 5))
            else:
                self.status_label.configure(text="Timeline playback complete")
        
        animate_playhead()
        
        # Update frame label during playback
        def update_frame_label(frame=0):
            if frame < 80:  # 4 seconds at 20fps
                self.frame_label.configure(text=str(frame))
                self.duration_label.configure(text=f"{frame//20}:{(frame%20)*3:02d}")
                self.after(50, lambda: update_frame_label(frame + 1))
        
        update_frame_label()

    def stop_timeline(self):
        """Stop timeline animation."""
        self.timeline_canvas.delete("playhead")
        self.status_label.configure(text="Timeline stopped")
        self.frame_label.configure(text="0")
        self.duration_label.configure(text="0:00")

    def add_fade_in(self):
        """Add fade in animation."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            animation = {
                'type': 'fade_in',
                'duration': self.anim_duration_var.get(),
                'easing': self.easing_var.get(),
                'properties': {'opacity': {'from': 0, 'to': 1}}
            }
            asset['animations'].append(animation)
            self.status_label.configure(text=f"Added fade in animation to {asset['name']}")
            messagebox.showinfo("Success", "Fade in animation added!")

    def add_slide_in(self):
        """Add slide in animation."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            animation = {
                'type': 'slide_in',
                'duration': self.anim_duration_var.get(),
                'easing': self.easing_var.get(),
                'properties': {
                    'x': {'from': -100, 'to': asset['properties']['x']}
                }
            }
            asset['animations'].append(animation)
            self.status_label.configure(text=f"Added slide in animation to {asset['name']}")
            messagebox.showinfo("Success", "Slide in animation added!")

    def add_scale_up(self):
        """Add scale up animation."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            animation = {
                'type': 'scale_up',
                'duration': self.anim_duration_var.get(),
                'easing': self.easing_var.get(),
                'properties': {
                    'width': {'from': 0, 'to': asset['properties']['width']},
                    'height': {'from': 0, 'to': asset['properties']['height']}
                }
            }
            asset['animations'].append(animation)
            self.status_label.configure(text=f"Added scale up animation to {asset['name']}")
            messagebox.showinfo("Success", "Scale up animation added!")

    def add_rotation(self):
        """Add rotation animation."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            animation = {
                'type': 'rotation',
                'duration': self.anim_duration_var.get(),
                'easing': self.easing_var.get(),
                'properties': {
                    'rotation': {'from': 0, 'to': 360}
                }
            }
            asset['animations'].append(animation)
            self.status_label.configure(text=f"Added rotation animation to {asset['name']}")
            messagebox.showinfo("Success", "Rotation animation added!")

    def add_bounce(self):
        """Add bounce animation."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            animation = {
                'type': 'bounce',
                'duration': self.anim_duration_var.get(),
                'easing': 'bounce',
                'properties': {
                    'y': {'from': asset['properties']['y'] - 50, 'to': asset['properties']['y']}
                }
            }
            asset['animations'].append(animation)
            self.status_label.configure(text=f"Added bounce animation to {asset['name']}")
            messagebox.showinfo("Success", "Bounce animation added!")

    def add_elastic(self):
        """Add elastic animation."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            animation = {
                'type': 'elastic',
                'duration': self.anim_duration_var.get(),
                'easing': 'elastic',
                'properties': {
                    'width': {'from': asset['properties']['width'] * 1.5, 'to': asset['properties']['width']},
                    'height': {'from': asset['properties']['height'] * 1.5, 'to': asset['properties']['height']}
                }
            }
            asset['animations'].append(animation)
            self.status_label.configure(text=f"Added elastic animation to {asset['name']}")
            messagebox.showinfo("Success", "Elastic animation added!")

    def add_brightness_effect(self):
        """Add brightness effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'brightness',
                'strength': self.effect_strength_var.get(),
                'parameters': {'value': 1.2}  # 20% brighter
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Brightness ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added brightness effect to {asset['name']}")
            messagebox.showinfo("Success", "Brightness effect added!")

    def add_contrast_effect(self):
        """Add contrast effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'contrast',
                'strength': self.effect_strength_var.get(),
                'parameters': {'value': 1.3}  # 30% more contrast
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Contrast ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added contrast effect to {asset['name']}")
            messagebox.showinfo("Success", "Contrast effect added!")

    def add_saturation_effect(self):
        """Add saturation effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'saturation',
                'strength': self.effect_strength_var.get(),
                'parameters': {'value': 1.4}  # 40% more saturated
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Saturation ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added saturation effect to {asset['name']}")
            messagebox.showinfo("Success", "Saturation effect added!")

    def add_hue_rotate_effect(self):
        """Add hue rotate effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'hue-rotate',
                'strength': self.effect_strength_var.get(),
                'parameters': {'degrees': 90}  # 90 degree hue rotation
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Hue Rotate ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added hue rotate effect to {asset['name']}")
            messagebox.showinfo("Success", "Hue rotate effect added!")

    def add_sepia_effect(self):
        """Add sepia effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'sepia',
                'strength': self.effect_strength_var.get(),
                'parameters': {'value': 0.8}  # 80% sepia
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Sepia ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added sepia effect to {asset['name']}")
            messagebox.showinfo("Success", "Sepia effect added!")

    def add_grayscale_effect(self):
        """Add grayscale effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'grayscale',
                'strength': self.effect_strength_var.get(),
                'parameters': {'value': 1.0}  # Full grayscale
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Grayscale ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added grayscale effect to {asset['name']}")
            messagebox.showinfo("Success", "Grayscale effect added!")

    def add_blur_effect(self):
        """Add blur effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'blur',
                'strength': self.effect_strength_var.get(),
                'parameters': {'radius': 5}  # 5px blur radius
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Blur ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added blur effect to {asset['name']}")
            messagebox.showinfo("Success", "Blur effect added!")

    def add_shadow_effect(self):
        """Add shadow effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'drop-shadow',
                'strength': self.effect_strength_var.get(),
                'parameters': {
                    'x': 5, 'y': 5, 'blur': 10, 
                    'color': 'rgba(0,0,0,0.5)'
                }
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Drop Shadow ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added drop shadow effect to {asset['name']}")
            messagebox.showinfo("Success", "Drop shadow effect added!")

    def add_glow_effect(self):
        """Add glow effect."""
        if not self.selected_asset_id:
            messagebox.showwarning("No Selection", "Please select an asset first.")
            return
        
        asset = self.media_assets.get(self.selected_asset_id)
        if asset:
            effect = {
                'type': 'glow',
                'strength': self.effect_strength_var.get(),
                'parameters': {
                    'blur': 15, 'color': '#ffff00',
                    'intensity': 0.8
                }
            }
            asset['effects'].append(effect)
            self.effects_listbox.insert(tk.END, f"Glow ({effect['strength']:.1f})")
            self.status_label.configure(text=f"Added glow effect to {asset['name']}")
            messagebox.showinfo("Success", "Glow effect added!")

    def update_effect_strength(self, value):
        """Update effect strength."""
        self.status_label.configure(text=f"Effect strength: {float(value):.1f}")
        
        # Update the most recent effect if an asset is selected
        if self.selected_asset_id:
            asset = self.media_assets.get(self.selected_asset_id)
            if asset and asset['effects']:
                # Update the last effect's strength
                asset['effects'][-1]['strength'] = float(value)

    def browse_audio_file(self, var, title):
        """Browse for audio file."""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title=f"Select {title}",
            filetypes=filetypes,
            parent=self
        )
        
        if filepath:
            var.set(filepath)

    def export_html_game(self):
        """Export complete HTML game with media."""
        if self.app_ref:
            self.app_ref.export_game_handler()
        self.status_label.configure(text="Exported HTML game")

    def export_media_pack(self):
        """Export media pack."""
        messagebox.showinfo("Export", "Media pack export feature coming soon!")

    def export_asset_library(self):
        """Export asset library."""
        messagebox.showinfo("Export", "Asset library export feature coming soon!")

    def apply_and_preview(self):
        """Apply changes and open preview."""
        if self.current_node and self.app_ref:
            # Save any pending changes
            if hasattr(self.app_ref, 'state_manager'):
                self.app_ref.state_manager.save_state("Advanced media updated")
            
            # Open preview
            if hasattr(self.app_ref, 'preview_toolbar'):
                try:
                    self.app_ref.preview_toolbar.preview_controls._open_preview()
                except:
                    pass
            
            self.status_label.configure(text="Changes applied - Preview opened")
            messagebox.showinfo("Success", "Media changes applied and preview opened!")

    def draw_initial_timeline(self):
        """Draw the initial timeline layout."""
        try:
            canvas_width = self.timeline_canvas.winfo_width()
            if canvas_width <= 1:
                canvas_width = 600  # Default width
            
            # Clear canvas
            self.timeline_canvas.delete("all")
            
            # Draw time ruler
            for i in range(0, canvas_width, 60):
                time_sec = i // 60
                self.timeline_canvas.create_line(i, 0, i, 20, fill="#666666", width=1)
                self.timeline_canvas.create_text(i + 5, 10, text=f"{time_sec}s", fill="#ffffff", anchor="w", font=("Arial", 8))
            
            # Draw track backgrounds
            tracks = ["Background", "Foreground", "Effects", "Audio"]
            track_height = 50
            
            for i, track in enumerate(tracks):
                y = 25 + i * track_height
                
                # Track label background
                self.timeline_canvas.create_rectangle(
                    0, y, 80, y + track_height - 5, 
                    fill="#3a3a3a", outline="#555555", width=1
                )
                
                # Track label text
                self.timeline_canvas.create_text(
                    5, y + track_height//2 - 2, 
                    text=track, fill="#ffffff", anchor="w", font=("Arial", 9)
                )
                
                # Track timeline area
                self.timeline_canvas.create_rectangle(
                    80, y, canvas_width, y + track_height - 5,
                    fill="#2a2a2a", outline="#555555", width=1
                )
            
            # Add some sample timeline items
            self.timeline_canvas.create_rectangle(
                100, 30, 180, 65, 
                fill="#4CAF50", outline="#2E7D32", width=2
            )
            self.timeline_canvas.create_text(
                140, 47, text="Image", fill="white", font=("Arial", 8, "bold")
            )
            
            self.timeline_canvas.create_rectangle(
                200, 80, 300, 115, 
                fill="#2196F3", outline="#1565C0", width=2
            )
            self.timeline_canvas.create_text(
                250, 97, text="Animation", fill="white", font=("Arial", 8, "bold")
            )
            
            self.timeline_canvas.create_rectangle(
                120, 180, 250, 215, 
                fill="#FF9800", outline="#E65100", width=2
            )
            self.timeline_canvas.create_text(
                185, 197, text="Audio", fill="white", font=("Arial", 8, "bold")
            )
            
        except Exception as e:
            print(f"Error drawing timeline: {e}")