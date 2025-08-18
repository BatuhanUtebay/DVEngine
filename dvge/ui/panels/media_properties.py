# dvge/ui/panels/media_properties.py

"""Advanced Media Properties Panel for DVGE - Supports videos, animations, keyframes, and effects."""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
from typing import TYPE_CHECKING, Dict, List, Optional, Any

if TYPE_CHECKING:
    from ...core.application import DVGApp
    from ...features.media_system import MediaAsset, MediaLibrary

try:
    from ...features.media_system import (
        MediaLibrary, MediaAsset, MediaType, AnimationType, EasingType,
        AnimationEngine, EffectsEngine, MediaPresets
    )
    from ...constants import *
    MEDIA_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Media system not available: {e}")
    MEDIA_SYSTEM_AVAILABLE = False
    # Fallback constants
    COLOR_ACCENT = "#1f538d"
    COLOR_ACCENT_HOVER = "#1e4d82"


class MediaPropertiesPanel(ctk.CTkFrame):
    """Advanced properties panel for managing node media assets."""

    def __init__(self, parent, app_ref=None, on_change_callback=None):
        super().__init__(parent)
        self.app_ref: 'DVGApp' = app_ref
        self.on_change_callback = on_change_callback
        self.current_node = None
        self._ignore_changes = False

        # Debug media system availability (optional debug info)
        # print(f"Media system available: {MEDIA_SYSTEM_AVAILABLE}")
        # if app_ref:
        #     print(f"App has media_library: {hasattr(app_ref, 'media_library')}")

        # Media library reference
        self.media_library: Optional['MediaLibrary'] = None
        if self.app_ref and hasattr(self.app_ref, 'media_library'):
            self.media_library = self.app_ref.media_library

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components."""
        # Check if media system is available
        if not MEDIA_SYSTEM_AVAILABLE:
            error_frame = ctk.CTkFrame(self)
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text="⚠️ Media System Error",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="orange"
            )
            error_label.pack(pady=(20, 10))
            
            detail_label = ctk.CTkLabel(
                error_frame,
                text="The advanced media system could not be loaded.\nUsing fallback mode with basic functionality.",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            detail_label.pack(pady=(0, 10))
            
            # Still show basic functionality
            self._setup_basic_mode()
            return

        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Advanced Media",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20), padx=20)

        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=500)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        try:
            self.setup_mode_selection()
            self.setup_asset_management()
            self.setup_asset_list()
            self.setup_asset_properties()
            self.setup_animation_controls()
            self.setup_effects_controls()
            self.setup_timeline_editor()
            self.setup_preset_buttons()
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"UI Setup Error: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="orange"
            )
            error_label.pack(pady=20, padx=20)

    def setup_mode_selection(self):
        """Setup legacy/advanced mode selection."""
        mode_frame = ctk.CTkFrame(self.scroll_frame)
        mode_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            mode_frame,
            text="Media Mode",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        self.legacy_mode_var = ctk.BooleanVar()
        self.legacy_checkbox = ctk.CTkCheckBox(
            mode_frame,
            text="Use Legacy Mode (Simple background/audio only)",
            variable=self.legacy_mode_var,
            command=self._on_mode_change
        )
        self.legacy_checkbox.pack(anchor="w", padx=10, pady=5)

        # Info label
        self.mode_info_label = ctk.CTkLabel(
            mode_frame,
            text="Advanced mode supports videos, animations, keyframes, and effects",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.mode_info_label.pack(padx=10, pady=(0, 10))

    def setup_asset_management(self):
        """Setup asset import/management section."""
        asset_mgmt_frame = ctk.CTkFrame(self.scroll_frame)
        asset_mgmt_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            asset_mgmt_frame,
            text="Asset Management",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Asset import buttons
        buttons_frame = ctk.CTkFrame(asset_mgmt_frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        if MEDIA_SYSTEM_AVAILABLE:
            image_type = MediaType.IMAGE
            video_type = MediaType.VIDEO
            audio_type = MediaType.AUDIO
        else:
            image_type = "image"
            video_type = "video"
            audio_type = "audio"

        ctk.CTkButton(
            buttons_frame,
            text="Import Image",
            command=lambda: self._import_asset(image_type),
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Import Video",
            command=lambda: self._import_asset(video_type),
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Import Audio",
            command=lambda: self._import_asset(audio_type),
            width=120
        ).pack(side="left", padx=5)

        # Asset library button
        ctk.CTkButton(
            asset_mgmt_frame,
            text="Open Asset Library",
            command=self._open_asset_library,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER
        ).pack(pady=10)

    def setup_asset_list(self):
        """Setup list of assets in current node."""
        list_frame = ctk.CTkFrame(self.scroll_frame)
        list_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            list_frame,
            text="Node Media Assets",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Asset list with scrollbar
        self.asset_listbox = tk.Listbox(
            list_frame,
            height=4,
            selectmode=tk.SINGLE,
            font=("Arial", 10)
        )
        self.asset_listbox.pack(fill="x", padx=10, pady=5)
        self.asset_listbox.bind("<<ListboxSelect>>", self._on_asset_select)

        # Asset control buttons
        asset_controls = ctk.CTkFrame(list_frame)
        asset_controls.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            asset_controls,
            text="Move Up",
            command=self._move_asset_up,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            asset_controls,
            text="Move Down",
            command=self._move_asset_down,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            asset_controls,
            text="Remove",
            command=self._remove_selected_asset,
            width=100,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="right", padx=5)

    def setup_asset_properties(self):
        """Setup properties for selected asset."""
        self.props_frame = ctk.CTkFrame(self.scroll_frame)
        self.props_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.props_frame,
            text="Asset Properties",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Asset info
        self.asset_info_label = ctk.CTkLabel(
            self.props_frame,
            text="Select an asset to edit its properties",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.asset_info_label.pack(pady=5)

        # Transform properties
        transform_frame = ctk.CTkFrame(self.props_frame)
        transform_frame.pack(fill="x", padx=10, pady=5)

        # Position
        pos_frame = ctk.CTkFrame(transform_frame)
        pos_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(pos_frame, text="Position (%):",
                     width=80).pack(side="left", padx=5)

        self.x_var = ctk.DoubleVar(value=0)
        self.x_entry = ctk.CTkEntry(
            pos_frame, textvariable=self.x_var, width=60)
        self.x_entry.pack(side="left", padx=2)
        self.x_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(pos_frame, text="x", width=20).pack(side="left")

        self.y_var = ctk.DoubleVar(value=0)
        self.y_entry = ctk.CTkEntry(
            pos_frame, textvariable=self.y_var, width=60)
        self.y_entry.pack(side="left", padx=2)
        self.y_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(pos_frame, text="y").pack(side="left")

        # Size
        size_frame = ctk.CTkFrame(transform_frame)
        size_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(size_frame, text="Size (%):",
                     width=80).pack(side="left", padx=5)

        self.width_var = ctk.DoubleVar(value=100)
        self.width_entry = ctk.CTkEntry(
            size_frame, textvariable=self.width_var, width=60)
        self.width_entry.pack(side="left", padx=2)
        self.width_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(size_frame, text="w", width=20).pack(side="left")

        self.height_var = ctk.DoubleVar(value=100)
        self.height_entry = ctk.CTkEntry(
            size_frame, textvariable=self.height_var, width=60)
        self.height_entry.pack(side="left", padx=2)
        self.height_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(size_frame, text="h").pack(side="left")

        # Rotation and Opacity
        rot_opacity_frame = ctk.CTkFrame(transform_frame)
        rot_opacity_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(rot_opacity_frame, text="Rotation:",
                     width=80).pack(side="left", padx=5)
        self.rotation_var = ctk.DoubleVar(value=0)
        self.rotation_entry = ctk.CTkEntry(
            rot_opacity_frame, textvariable=self.rotation_var, width=60)
        self.rotation_entry.pack(side="left", padx=2)
        self.rotation_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(rot_opacity_frame, text="Opacity:",
                     width=60).pack(side="left", padx=(20, 5))
        self.opacity_var = ctk.DoubleVar(value=1.0)
        self.opacity_entry = ctk.CTkEntry(
            rot_opacity_frame, textvariable=self.opacity_var, width=60)
        self.opacity_entry.pack(side="left", padx=2)
        self.opacity_entry.bind("<KeyRelease>", self._on_property_change)

        # Playback controls (for video/audio)
        self.playback_frame = ctk.CTkFrame(self.props_frame)
        self.playback_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.playback_frame,
            text="Playback Settings",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Checkboxes
        playback_checks = ctk.CTkFrame(self.playback_frame)
        playback_checks.pack(fill="x", padx=5, pady=5)

        self.autoplay_var = ctk.BooleanVar()
        self.autoplay_check = ctk.CTkCheckBox(
            playback_checks,
            text="Autoplay",
            variable=self.autoplay_var,
            command=self._on_property_change
        )
        self.autoplay_check.pack(side="left", padx=10)

        self.loop_var = ctk.BooleanVar()
        self.loop_check = ctk.CTkCheckBox(
            playback_checks,
            text="Loop",
            variable=self.loop_var,
            command=self._on_property_change
        )
        self.loop_check.pack(side="left", padx=10)

        self.muted_var = ctk.BooleanVar()
        self.muted_check = ctk.CTkCheckBox(
            playback_checks,
            text="Muted",
            variable=self.muted_var,
            command=self._on_property_change
        )
        self.muted_check.pack(side="left", padx=10)

        # Volume and timing
        volume_timing = ctk.CTkFrame(self.playback_frame)
        volume_timing.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(volume_timing, text="Volume:",
                     width=60).pack(side="left", padx=5)
        self.volume_var = ctk.DoubleVar(value=1.0)
        self.volume_entry = ctk.CTkEntry(
            volume_timing, textvariable=self.volume_var, width=60)
        self.volume_entry.pack(side="left", padx=2)
        self.volume_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(volume_timing, text="Start Time:",
                     width=80).pack(side="left", padx=(20, 5))
        self.start_time_var = ctk.DoubleVar(value=0)
        self.start_time_entry = ctk.CTkEntry(
            volume_timing, textvariable=self.start_time_var, width=60)
        self.start_time_entry.pack(side="left", padx=2)
        self.start_time_entry.bind("<KeyRelease>", self._on_property_change)

    def setup_animation_controls(self):
        """Setup animation timeline and keyframe controls."""
        self.anim_frame = ctk.CTkFrame(self.scroll_frame)
        self.anim_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.anim_frame,
            text="Animations & Keyframes",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Animation type selection
        anim_type_frame = ctk.CTkFrame(self.anim_frame)
        anim_type_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(anim_type_frame, text="Animation Type:").pack(
            side="left", padx=5)

        self.animation_type_var = ctk.StringVar(value="fade")
        self.animation_type_combo = ctk.CTkComboBox(
            anim_type_frame,
            variable=self.animation_type_var,
            values=["fade", "slide", "scale", "rotate", "custom"],
            command=self._on_animation_type_change
        )
        self.animation_type_combo.pack(side="left", padx=10)

        ctk.CTkButton(
            anim_type_frame,
            text="Add Animation",
            command=self._add_animation,
            width=120
        ).pack(side="right", padx=5)

        # Animation list
        self.animation_listbox = tk.Listbox(
            self.anim_frame,
            height=3,
            selectmode=tk.SINGLE,
            font=("Arial", 9)
        )
        self.animation_listbox.pack(fill="x", padx=10, pady=5)

        # Timeline controls (simplified for now)
        timeline_frame = ctk.CTkFrame(self.anim_frame)
        timeline_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(timeline_frame, text="Duration (s):").pack(
            side="left", padx=5)
        self.duration_var = ctk.DoubleVar(value=1.0)
        self.duration_entry = ctk.CTkEntry(
            timeline_frame, textvariable=self.duration_var, width=80)
        self.duration_entry.pack(side="left", padx=5)

        ctk.CTkLabel(timeline_frame, text="Easing:").pack(
            side="left", padx=(20, 5))
        self.easing_var = ctk.StringVar(value="ease-in-out")
        self.easing_combo = ctk.CTkComboBox(
            timeline_frame,
            variable=self.easing_var,
            values=["linear", "ease-in", "ease-out",
                    "ease-in-out", "bounce", "elastic"],
            width=120
        )
        self.easing_combo.pack(side="left", padx=5)

    def setup_effects_controls(self):
        """Setup visual effects controls."""
        self.effects_frame = ctk.CTkFrame(self.scroll_frame)
        self.effects_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.effects_frame,
            text="Visual Effects",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Effect type selection
        effect_type_frame = ctk.CTkFrame(self.effects_frame)
        effect_type_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(effect_type_frame, text="Effect Type:").pack(
            side="left", padx=5)

        self.effect_type_var = ctk.StringVar(value="blur")
        self.effect_type_combo = ctk.CTkComboBox(
            effect_type_frame,
            variable=self.effect_type_var,
            values=["blur", "brightness", "contrast",
                    "hue-rotate", "saturate", "sepia", "drop-shadow"],
            command=self._on_effect_type_change
        )
        self.effect_type_combo.pack(side="left", padx=10)

        ctk.CTkLabel(effect_type_frame, text="Strength:").pack(
            side="left", padx=(20, 5))
        self.effect_strength_var = ctk.DoubleVar(value=1.0)
        self.effect_strength_entry = ctk.CTkEntry(
            effect_type_frame,
            textvariable=self.effect_strength_var,
            width=80
        )
        self.effect_strength_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            effect_type_frame,
            text="Add Effect",
            command=self._add_effect,
            width=100
        ).pack(side="right", padx=5)

        # Effects list
        self.effects_listbox = tk.Listbox(
            self.effects_frame,
            height=3,
            selectmode=tk.SINGLE,
            font=("Arial", 9)
        )
        self.effects_listbox.pack(fill="x", padx=10, pady=5)

    def setup_timeline_editor(self):
        """Setup the timeline and keyframe editor."""
        self.timeline_frame = ctk.CTkFrame(self.scroll_frame)
        self.timeline_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            self.timeline_frame,
            text="Timeline & Keyframe Editor",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Timeline editor toggle
        self.timeline_visible_var = ctk.BooleanVar()
        timeline_toggle = ctk.CTkCheckBox(
            self.timeline_frame,
            text="Show Timeline Editor",
            variable=self.timeline_visible_var,
            command=self._toggle_timeline_editor
        )
        timeline_toggle.pack(anchor="w", padx=10, pady=5)

        # Timeline editor container (initially hidden)
        self.timeline_container = ctk.CTkFrame(self.timeline_frame)
        # Don't pack initially - will be shown when toggled

        # Import and create timeline editor
        try:
            from ..widgets.timeline_editor import TimelineEditor
            self.timeline_editor = TimelineEditor(
                self.timeline_container,
                on_change_callback=self.on_change_callback
            )
            self.timeline_editor.pack(fill="both", expand=True, padx=5, pady=5)
        except ImportError as e:
            # Fallback if timeline editor can't be imported
            error_label = ctk.CTkLabel(
                self.timeline_container,
                text=f"Timeline editor not available: {e}",
                text_color="orange"
            )
            error_label.pack(pady=20)
            self.timeline_editor = None

        # Quick timeline controls (always visible)
        quick_timeline = ctk.CTkFrame(self.timeline_frame)
        quick_timeline.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            quick_timeline,
            text="Open Advanced Timeline",
            command=self._open_timeline_window,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            quick_timeline,
            text="Clear All Animations",
            command=self._clear_all_animations,
            width=150,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="right", padx=5)

    def setup_preset_buttons(self):
        """Setup preset animation/effect buttons."""
        preset_frame = ctk.CTkFrame(self.scroll_frame)
        preset_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            preset_frame,
            text="Quick Presets",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)

        # Preset buttons in rows
        presets_row1 = ctk.CTkFrame(preset_frame)
        presets_row1.pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(
            presets_row1,
            text="Telltale Fade",
            command=lambda: self._apply_preset("telltale_fade"),
            width=120
        ).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            presets_row1,
            text="Dramatic Slide",
            command=lambda: self._apply_preset("dramatic_slide"),
            width=120
        ).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            presets_row1,
            text="Zoom Reveal",
            command=lambda: self._apply_preset("zoom_reveal"),
            width=120
        ).pack(side="left", padx=5, expand=True, fill="x")

        presets_row2 = ctk.CTkFrame(preset_frame)
        presets_row2.pack(fill="x", padx=10, pady=2)

        ctk.CTkButton(
            presets_row2,
            text="Mystery Blur",
            command=lambda: self._apply_preset("mystery_blur"),
            width=120
        ).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            presets_row2,
            text="Sepia Memory",
            command=lambda: self._apply_preset("sepia_memory"),
            width=120
        ).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            presets_row2,
            text="Action Scene",
            command=lambda: self._apply_preset("action_scene"),
            width=120
        ).pack(side="left", padx=5, expand=True, fill="x")

    # Event handlers and core methods
    def _on_mode_change(self):
        """Handle legacy/advanced mode change."""
        if not self.current_node:
            return

        is_legacy = self.legacy_mode_var.get()
        self.current_node.legacy_mode = is_legacy
        self.current_node.media_enabled = not is_legacy

        # Update UI visibility
        self._update_ui_visibility()

        if self.on_change_callback:
            self.on_change_callback()

    def _update_ui_visibility(self):
        """Update UI component visibility based on mode."""
        is_legacy = self.legacy_mode_var.get()

        # Hide/show advanced components
        components_to_hide = [
            self.props_frame, self.anim_frame, self.effects_frame
        ]

        for component in components_to_hide:
            if is_legacy:
                component.pack_forget()
            else:
                component.pack(fill="x", padx=10, pady=5)

    def _import_asset(self, media_type):
        """Import a new media asset."""
        if not MEDIA_SYSTEM_AVAILABLE:
            messagebox.showerror("Error", "Media system not available")
            return

        if not self.media_library:
            messagebox.showerror("Error", "Media library not available")
            return

        # File dialog based on media type
        if hasattr(MediaType, 'IMAGE'):
            file_types = {
                MediaType.IMAGE: [("Image files", "*.png *.jpg *.jpeg *.gif *.webp")],
                MediaType.VIDEO: [("Video files", "*.mp4 *.webm *.ogg *.avi *.mov")],
                MediaType.AUDIO: [("Audio files", "*.mp3 *.wav *.ogg *.m4a")]
            }
        else:
            # Fallback for when MediaType is not available
            file_types = {
                "image": [("Image files", "*.png *.jpg *.jpeg *.gif *.webp")],
                "video": [("Video files", "*.mp4 *.webm *.ogg *.avi *.mov")],
                "audio": [("Audio files", "*.mp3 *.wav *.ogg *.m4a")]
            }

        try:
            title = f"Import {media_type.value.title()}" if hasattr(
                media_type, 'value') else f"Import {str(media_type).title()}"
        except:
            title = "Import Media"

        filepath = filedialog.askopenfilename(
            title=title,
            filetypes=file_types.get(media_type, [("All files", "*.*")])
        )

        if filepath:
            asset = self.media_library.add_asset(filepath)
            if asset:
                # Add to current node
                if self.current_node:
                    self.current_node.add_media_asset(asset.asset_id)
                    self._update_asset_list()
                    if self.on_change_callback:
                        self.on_change_callback()
                messagebox.showinfo(
                    "Success", f"Asset '{asset.name}' imported successfully")
            else:
                messagebox.showerror(
                    "Error", "Failed to import asset. Unsupported format?")

    def _open_asset_library(self):
        """Open the asset library window."""
        if not self.media_library:
            messagebox.showerror("Error", "Media library not available")
            return

        # Import here to avoid circular imports
        from ..windows.asset_library_window import AssetLibraryWindow
        
        try:
            # Create and open asset library window
            library_window = AssetLibraryWindow(
                self,
                media_library=self.media_library,
                current_node=self.current_node,
                on_asset_selected=self._on_library_asset_selected
            )
            library_window.focus()
        except ImportError:
            messagebox.showerror("Error", "Asset library window not available yet. Creating it now...")
            self._create_asset_library_window()
    
    def _on_library_asset_selected(self, asset_id: str):
        """Handle asset selection from library."""
        if self.current_node:
            if asset_id not in self.current_node.media_assets:
                self.current_node.media_assets.append(asset_id)
                self._update_asset_list()
                if self.on_change_callback:
                    self.on_change_callback()
    
    def _create_asset_library_window(self):
        """Create a simple asset library dialog."""
        if not self.media_library:
            return
            
        # Create a simple selection dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Asset Library")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Title
        ctk.CTkLabel(
            dialog, 
            text="Asset Library", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Asset list
        listframe = ctk.CTkFrame(dialog)
        listframe.pack(fill="both", expand=True, padx=20, pady=10)
        
        asset_list = tk.Listbox(listframe, font=("Arial", 11))
        asset_list.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Populate list
        for asset_id, asset in self.media_library.assets.items():
            display = f"[{asset.media_type.value.upper()}] {asset.name}"
            asset_list.insert(tk.END, display)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def add_selected():
            selection = asset_list.curselection()
            if selection and self.current_node:
                asset_ids = list(self.media_library.assets.keys())
                selected_asset_id = asset_ids[selection[0]]
                self._on_library_asset_selected(selected_asset_id)
                dialog.destroy()
        
        ctk.CTkButton(
            button_frame, 
            text="Add to Node", 
            command=add_selected
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        ).pack(side="right", padx=10)

    def _update_asset_list(self):
        """Update the asset list display."""
        self.asset_listbox.delete(0, tk.END)

        if self.current_node and self.media_library:
            for asset_id in self.current_node.media_assets:
                asset = self.media_library.get_asset(asset_id)
                if asset:
                    display_name = f"[{asset.media_type.value.upper()}] {asset.name}"
                    self.asset_listbox.insert(tk.END, display_name)

    def _on_asset_select(self, event):
        """Handle asset selection in list."""
        selection = self.asset_listbox.curselection()
        if selection and self.current_node and self.media_library:
            index = selection[0]
            if index < len(self.current_node.media_assets):
                asset_id = self.current_node.media_assets[index]
                asset = self.media_library.get_asset(asset_id)
                if asset:
                    self._load_asset_properties(asset)

    def _load_asset_properties(self, asset: 'MediaAsset'):
        """Load asset properties into the UI."""
        self._ignore_changes = True

        try:
            # Update asset info
            self.asset_info_label.configure(
                text=f"Editing: {asset.name} ({asset.media_type.value})"
            )

            # Load transform properties
            self.x_var.set(asset.x)
            self.y_var.set(asset.y)
            self.width_var.set(asset.width)
            self.height_var.set(asset.height)
            self.rotation_var.set(asset.rotation)
            self.opacity_var.set(asset.opacity)

            # Load playback properties
            self.autoplay_var.set(asset.autoplay)
            self.loop_var.set(asset.loop)
            self.muted_var.set(asset.muted)
            self.volume_var.set(asset.volume)
            self.start_time_var.set(asset.start_time)

            # Update animations list
            self.animation_listbox.delete(0, tk.END)
            for anim in asset.animations:
                self.animation_listbox.insert(
                    tk.END, f"{anim.get('type', 'custom')} - {anim.get('duration', 0)}s")

            # Update effects list
            self.effects_listbox.delete(0, tk.END)
            for effect in asset.effects:
                self.effects_listbox.insert(
                    tk.END, f"{effect.effect_type}: {effect.value}")

        finally:
            self._ignore_changes = False

    def _on_property_change(self, event=None):
        """Handle property changes."""
        if self._ignore_changes:
            return

        # Get selected asset
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node or not self.media_library:
            return

        index = selection[0]
        if index >= len(self.current_node.media_assets):
            return

        asset_id = self.current_node.media_assets[index]
        asset = self.media_library.get_asset(asset_id)
        if not asset:
            return

        try:
            # Update asset properties
            asset.x = self.x_var.get()
            asset.y = self.y_var.get()
            asset.width = self.width_var.get()
            asset.height = self.height_var.get()
            asset.rotation = self.rotation_var.get()
            asset.opacity = self.opacity_var.get()

            asset.autoplay = self.autoplay_var.get()
            asset.loop = self.loop_var.get()
            asset.muted = self.muted_var.get()
            asset.volume = self.volume_var.get()
            asset.start_time = self.start_time_var.get()

            if self.on_change_callback:
                self.on_change_callback()

        except (ValueError, tk.TclError):
            pass  # Handle invalid input gracefully

    def _move_asset_up(self):
        """Move selected asset up in the list."""
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node:
            return

        index = selection[0]
        if index > 0:
            # Swap assets
            assets = self.current_node.media_assets
            assets[index], assets[index-1] = assets[index-1], assets[index]
            self._update_asset_list()
            self.asset_listbox.selection_set(index - 1)

            if self.on_change_callback:
                self.on_change_callback()

    def _move_asset_down(self):
        """Move selected asset down in the list."""
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node:
            return

        index = selection[0]
        if index < len(self.current_node.media_assets) - 1:
            # Swap assets
            assets = self.current_node.media_assets
            assets[index], assets[index+1] = assets[index+1], assets[index]
            self._update_asset_list()
            self.asset_listbox.selection_set(index + 1)

            if self.on_change_callback:
                self.on_change_callback()

    def _remove_selected_asset(self):
        """Remove the selected asset from the node."""
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node:
            return

        index = selection[0]
        if index < len(self.current_node.media_assets):
            asset_id = self.current_node.media_assets[index]
            if self.media_library:
                asset = self.media_library.get_asset(asset_id)
                asset_name = asset.name if asset else "Unknown"
            else:
                asset_name = asset_id

            if messagebox.askyesno("Confirm", f"Remove '{asset_name}' from this node?"):
                self.current_node.media_assets.pop(index)
                self._update_asset_list()
                self.asset_info_label.configure(
                    text="Select an asset to edit its properties")

                if self.on_change_callback:
                    self.on_change_callback()

    def _add_animation(self):
        """Add an animation to the selected asset."""
        # Get selected asset
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node or not self.media_library:
            messagebox.showerror("Error", "Please select an asset first")
            return

        index = selection[0]
        if index >= len(self.current_node.media_assets):
            return

        asset_id = self.current_node.media_assets[index]
        asset = self.media_library.get_asset(asset_id)
        if not asset:
            return

        try:
            animation_type = self.animation_type_var.get()
            duration = self.duration_var.get()
            easing = self.easing_var.get()

            if MEDIA_SYSTEM_AVAILABLE:
                # Create animation based on type
                if animation_type == "fade":
                    animation = AnimationEngine.create_fade_animation(duration, 0, 1)
                elif animation_type == "slide":
                    animation = AnimationEngine.create_slide_animation(
                        duration, (-100, 0), (0, 0))
                elif animation_type == "scale":
                    animation = AnimationEngine.create_scale_animation(duration, 0.1, 1)
                elif animation_type == "rotate":
                    animation = AnimationEngine.create_rotation_animation(
                        duration, 0, 360)
                else:  # custom
                    animation = {
                        'type': 'custom',
                        'duration': duration,
                        'keyframes': []
                    }

                animation['easing'] = easing
                asset.animations.append(animation)

                # Update UI
                self._load_asset_properties(asset)

                if self.on_change_callback:
                    self.on_change_callback()

                messagebox.showinfo("Success", f"Added {animation_type} animation")

        except (ValueError, Exception) as e:
            messagebox.showerror("Error", f"Failed to add animation: {str(e)}")

    def _add_effect(self):
        """Add an effect to the selected asset."""
        # Get selected asset
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node or not self.media_library:
            messagebox.showerror("Error", "Please select an asset first")
            return

        index = selection[0]
        if index >= len(self.current_node.media_assets):
            return

        asset_id = self.current_node.media_assets[index]
        asset = self.media_library.get_asset(asset_id)
        if not asset:
            return

        try:
            effect_type = self.effect_type_var.get()
            strength = self.effect_strength_var.get()

            if MEDIA_SYSTEM_AVAILABLE:
                # Create effect based on type
                if effect_type == "blur":
                    effect = EffectsEngine.create_blur_effect(strength)
                elif effect_type == "brightness":
                    effect = EffectsEngine.create_brightness_effect(strength)
                elif effect_type == "contrast":
                    effect = EffectsEngine.create_contrast_effect(strength)
                elif effect_type == "hue-rotate":
                    effect = EffectsEngine.create_hue_rotate_effect(strength)
                elif effect_type == "saturate":
                    effect = EffectsEngine.create_saturate_effect(strength)
                elif effect_type == "sepia":
                    effect = EffectsEngine.create_sepia_effect(strength)
                elif effect_type == "drop-shadow":
                    effect = EffectsEngine.create_drop_shadow_effect(2, 2, strength, 'rgba(0,0,0,0.5)')
                else:
                    effect = MediaEffect(effect_type, strength)

                asset.effects.append(effect)

                # Update UI
                self._load_asset_properties(asset)

                if self.on_change_callback:
                    self.on_change_callback()

                messagebox.showinfo("Success", f"Added {effect_type} effect")

        except (ValueError, Exception) as e:
            messagebox.showerror("Error", f"Failed to add effect: {str(e)}")

    def _on_animation_type_change(self, value):
        """Handle animation type change."""
        pass  # Placeholder for future implementation

    def _on_effect_type_change(self, value):
        """Handle effect type change."""
        pass  # Placeholder for future implementation

    def _apply_preset(self, preset_name: str):
        """Apply a preset animation/effect configuration."""
        # Get selected asset
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node or not self.media_library:
            messagebox.showerror("Error", "Please select an asset first")
            return

        index = selection[0]
        if index >= len(self.current_node.media_assets):
            return

        asset_id = self.current_node.media_assets[index]
        asset = self.media_library.get_asset(asset_id)
        if not asset:
            return

        try:
            if MEDIA_SYSTEM_AVAILABLE:
                # Apply preset based on name
                if preset_name == "telltale_fade":
                    animation = MediaPresets.telltale_style_fade_in()
                    asset.animations.append(animation)
                    
                elif preset_name == "dramatic_slide":
                    animation = MediaPresets.dramatic_slide_in()
                    asset.animations.append(animation)
                    
                elif preset_name == "zoom_reveal":
                    animation = MediaPresets.zoom_reveal()
                    asset.animations.append(animation)
                    
                elif preset_name == "mystery_blur":
                    effects = MediaPresets.mystery_blur_in()
                    asset.effects.extend(effects)
                    
                elif preset_name == "sepia_memory":
                    effects = MediaPresets.sepia_memory_effect()
                    asset.effects.extend(effects)
                    
                elif preset_name == "action_scene":
                    effects = MediaPresets.action_scene_effects()
                    asset.effects.extend(effects)

                # Update UI
                self._load_asset_properties(asset)

                if self.on_change_callback:
                    self.on_change_callback()

                messagebox.showinfo("Success", f"Applied '{preset_name}' preset")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply preset: {str(e)}")

    def _toggle_timeline_editor(self):
        """Toggle timeline editor visibility."""
        if self.timeline_visible_var.get():
            self.timeline_container.pack(fill="both", expand=True, padx=10, pady=10)
            # Update with current selection
            selection = self.asset_listbox.curselection()
            if selection and self.current_node and self.media_library and self.timeline_editor:
                index = selection[0]
                if index < len(self.current_node.media_assets):
                    asset_id = self.current_node.media_assets[index]
                    asset = self.media_library.get_asset(asset_id)
                    if asset:
                        self.timeline_editor.load_asset(asset)
        else:
            self.timeline_container.pack_forget()

    def _open_timeline_window(self):
        """Open timeline editor in a separate window."""
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node or not self.media_library:
            messagebox.showerror("Error", "Please select an asset first")
            return

        index = selection[0]
        if index >= len(self.current_node.media_assets):
            return

        asset_id = self.current_node.media_assets[index]
        asset = self.media_library.get_asset(asset_id)
        if not asset:
            return

        try:
            from ..windows.timeline_window import TimelineWindow
            timeline_window = TimelineWindow(
                self,
                asset=asset,
                on_change_callback=self.on_change_callback
            )
            timeline_window.focus()
        except ImportError:
            # Create a simple timeline window
            self._create_simple_timeline_window(asset)

    def _create_simple_timeline_window(self, asset):
        """Create a simple timeline window."""
        window = ctk.CTkToplevel(self)
        window.title(f"Timeline Editor - {asset.name}")
        window.geometry("900x600")
        window.transient(self)

        # Import timeline editor
        try:
            from ..widgets.timeline_editor import TimelineEditor
            timeline_editor = TimelineEditor(
                window,
                asset=asset,
                on_change_callback=self.on_change_callback
            )
            timeline_editor.pack(fill="both", expand=True, padx=10, pady=10)
        except ImportError:
            ctk.CTkLabel(
                window,
                text="Timeline editor not available",
                font=ctk.CTkFont(size=16)
            ).pack(pady=50)

    def _clear_all_animations(self):
        """Clear all animations from selected asset."""
        selection = self.asset_listbox.curselection()
        if not selection or not self.current_node or not self.media_library:
            messagebox.showerror("Error", "Please select an asset first")
            return

        index = selection[0]
        if index >= len(self.current_node.media_assets):
            return

        asset_id = self.current_node.media_assets[index]
        asset = self.media_library.get_asset(asset_id)
        if not asset:
            return

        if messagebox.askyesno("Confirm", f"Clear all animations from '{asset.name}'?"):
            asset.animations.clear()
            self._load_asset_properties(asset)
            
            if self.timeline_editor:
                self.timeline_editor.load_asset(asset)

            if self.on_change_callback:
                self.on_change_callback()

    def load_node(self, node):
        """Load node data into the panel."""
        self.current_node = node
        self._ignore_changes = True

        try:
            if node:
                if MEDIA_SYSTEM_AVAILABLE:
                    # Load mode settings
                    if hasattr(self, 'legacy_mode_var'):
                        self.legacy_mode_var.set(getattr(node, 'legacy_mode', False))
                        self._update_ui_visibility()

                    # Update asset list
                    self._update_asset_list()
                else:
                    # Basic mode - load simple background and audio
                    if hasattr(self, 'bg_var'):
                        self.bg_var.set(getattr(node, 'backgroundImage', ''))
                    if hasattr(self, 'audio_var'):
                        self.audio_var.set(getattr(node, 'audio', ''))
            else:
                if MEDIA_SYSTEM_AVAILABLE:
                    if hasattr(self, 'legacy_mode_var'):
                        self.legacy_mode_var.set(False)
                    if hasattr(self, 'asset_listbox'):
                        self.asset_listbox.delete(0, tk.END)
                    if hasattr(self, 'asset_info_label'):
                        self.asset_info_label.configure(text="No node selected")
                else:
                    # Clear basic mode
                    if hasattr(self, 'bg_var'):
                        self.bg_var.set('')
                    if hasattr(self, 'audio_var'):
                        self.audio_var.set('')
        finally:
            self._ignore_changes = False

    def clear(self):
        """Clear the panel."""
        self.current_node = None
        self._ignore_changes = True
        try:
            self.legacy_mode_var.set(False)
            self.asset_listbox.delete(0, tk.END)
            self.animation_listbox.delete(0, tk.END)
            self.effects_listbox.delete(0, tk.END)
            self.asset_info_label.configure(text="No node selected")
        finally:
            self._ignore_changes = False

    def set_media_library(self, media_library: 'MediaLibrary'):
        """Set the media library reference."""
        self.media_library = media_library

    def _setup_basic_mode(self):
        """Setup basic media functionality when advanced system is not available."""
        basic_frame = ctk.CTkFrame(self)
        basic_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Basic background image
        bg_frame = ctk.CTkFrame(basic_frame)
        bg_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            bg_frame,
            text="Background Image",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        self.bg_var = ctk.StringVar()
        bg_entry = ctk.CTkEntry(
            bg_frame,
            textvariable=self.bg_var,
            placeholder_text="Path to background image..."
        )
        bg_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            bg_frame,
            text="Browse Image",
            command=self._browse_background_image
        ).pack(pady=5)
        
        # Basic audio
        audio_frame = ctk.CTkFrame(basic_frame)
        audio_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            audio_frame,
            text="Audio",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        self.audio_var = ctk.StringVar()
        audio_entry = ctk.CTkEntry(
            audio_frame,
            textvariable=self.audio_var,
            placeholder_text="Path to audio file..."
        )
        audio_entry.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            audio_frame,
            text="Browse Audio",
            command=self._browse_audio_file
        ).pack(pady=5)
    
    def _browse_background_image(self):
        """Browse for background image in basic mode."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.webp"), ("All files", "*.*")]
        )
        if filepath:
            self.bg_var.set(filepath)
            if self.current_node:
                self.current_node.backgroundImage = filepath
                if self.on_change_callback:
                    self.on_change_callback()
    
    def _browse_audio_file(self):
        """Browse for audio file in basic mode."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg *.m4a"), ("All files", "*.*")]
        )
        if filepath:
            self.audio_var.set(filepath)
            if self.current_node:
                self.current_node.audio = filepath
                if self.on_change_callback:
                    self.on_change_callback()
