# dvge/ui/widgets/timeline_editor.py

"""Advanced Timeline and Keyframe Editor for DVGE Media System."""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import math
from typing import Dict, List, Any, Optional, Tuple, Callable

try:
    from ...features.media_system import MediaAsset, Keyframe, EasingType
    MEDIA_SYSTEM_AVAILABLE = True
except ImportError:
    MEDIA_SYSTEM_AVAILABLE = False


class TimelineEditor(ctk.CTkFrame):
    """Advanced timeline editor with keyframe support."""

    def __init__(self, parent, asset: Optional['MediaAsset'] = None, 
                 on_change_callback: Optional[Callable] = None):
        super().__init__(parent)
        
        self.asset = asset
        self.on_change_callback = on_change_callback
        self.timeline_duration = 10.0  # seconds
        self.zoom_level = 1.0
        self.selected_keyframe = None
        self.dragging_keyframe = None
        self.playhead_position = 0.0
        
        # UI state
        self.timeline_canvas = None
        self.timeline_width = 600
        self.timeline_height = 300
        self.track_height = 40
        self.keyframe_radius = 6
        
        # Colors
        self.bg_color = "#2b2b2b"
        self.track_color = "#404040"
        self.keyframe_color = "#4a9eff"
        self.selected_keyframe_color = "#ff6b4a"
        self.playhead_color = "#ff4444"
        self.grid_color = "#555555"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the timeline editor UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Timeline & Keyframe Editor",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Control bar
        self.setup_control_bar()
        
        # Timeline canvas
        self.setup_timeline_canvas()
        
        # Properties panel
        self.setup_properties_panel()
        
    def setup_control_bar(self):
        """Setup timeline controls."""
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Playback controls
        play_frame = ctk.CTkFrame(control_frame)
        play_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(
            play_frame,
            text="⏮",
            width=30,
            command=self._go_to_start
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            play_frame,
            text="▶",
            width=30,
            command=self._play_pause
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            play_frame,
            text="⏯",
            width=30,
            command=self._stop
        ).pack(side="left", padx=2)
        
        # Timeline controls
        timeline_controls = ctk.CTkFrame(control_frame)
        timeline_controls.pack(side="left", padx=20)
        
        ctk.CTkLabel(timeline_controls, text="Duration:").pack(side="left", padx=5)
        self.duration_var = ctk.DoubleVar(value=self.timeline_duration)
        duration_entry = ctk.CTkEntry(
            timeline_controls, 
            textvariable=self.duration_var, 
            width=60
        )
        duration_entry.pack(side="left", padx=5)
        duration_entry.bind("<Return>", self._on_duration_change)
        
        ctk.CTkLabel(timeline_controls, text="Zoom:").pack(side="left", padx=(20, 5))
        zoom_slider = ctk.CTkSlider(
            timeline_controls,
            from_=0.1,
            to=5.0,
            number_of_steps=50,
            command=self._on_zoom_change
        )
        zoom_slider.set(self.zoom_level)
        zoom_slider.pack(side="left", padx=5)
        
        # Add keyframe button
        ctk.CTkButton(
            control_frame,
            text="+ Add Keyframe",
            command=self._add_keyframe_at_playhead
        ).pack(side="right", padx=10)
        
    def setup_timeline_canvas(self):
        """Setup the main timeline canvas."""
        canvas_frame = ctk.CTkFrame(self)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create canvas with scrollbars
        canvas_container = tk.Frame(canvas_frame, bg=self.bg_color)
        canvas_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.timeline_canvas = tk.Canvas(
            canvas_container,
            bg=self.bg_color,
            height=self.timeline_height,
            scrollregion=(0, 0, self.timeline_width * 2, self.timeline_height)
        )
        
        # Scrollbars
        h_scrollbar = tk.Scrollbar(
            canvas_container, 
            orient="horizontal", 
            command=self.timeline_canvas.xview
        )
        v_scrollbar = tk.Scrollbar(
            canvas_container, 
            orient="vertical", 
            command=self.timeline_canvas.yview
        )
        
        self.timeline_canvas.configure(
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        
        # Pack scrollbars and canvas
        h_scrollbar.pack(side="bottom", fill="x")
        v_scrollbar.pack(side="right", fill="y")
        self.timeline_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind events
        self.timeline_canvas.bind("<Button-1>", self._on_canvas_click)
        self.timeline_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.timeline_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.timeline_canvas.bind("<Double-Button-1>", self._on_canvas_double_click)
        
        # Initial draw
        self._draw_timeline()
        
    def setup_properties_panel(self):
        """Setup keyframe properties panel."""
        props_frame = ctk.CTkFrame(self)
        props_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            props_frame,
            text="Keyframe Properties",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        # Time and easing
        time_frame = ctk.CTkFrame(props_frame)
        time_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(time_frame, text="Time (s):").pack(side="left", padx=5)
        self.keyframe_time_var = ctk.DoubleVar()
        self.keyframe_time_entry = ctk.CTkEntry(
            time_frame,
            textvariable=self.keyframe_time_var,
            width=80
        )
        self.keyframe_time_entry.pack(side="left", padx=5)
        self.keyframe_time_entry.bind("<KeyRelease>", self._on_keyframe_property_change)
        
        ctk.CTkLabel(time_frame, text="Easing:").pack(side="left", padx=(20, 5))
        self.keyframe_easing_var = ctk.StringVar(value="ease-in-out")
        easing_combo = ctk.CTkComboBox(
            time_frame,
            variable=self.keyframe_easing_var,
            values=["linear", "ease-in", "ease-out", "ease-in-out", "bounce", "elastic"],
            command=self._on_keyframe_property_change
        )
        easing_combo.pack(side="left", padx=5)
        
        # Transform properties
        transform_frame = ctk.CTkFrame(props_frame)
        transform_frame.pack(fill="x", padx=10, pady=5)
        
        # Position
        ctk.CTkLabel(transform_frame, text="X:").pack(side="left", padx=5)
        self.kf_x_var = ctk.DoubleVar()
        ctk.CTkEntry(
            transform_frame, 
            textvariable=self.kf_x_var, 
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkLabel(transform_frame, text="Y:").pack(side="left", padx=5)
        self.kf_y_var = ctk.DoubleVar()
        ctk.CTkEntry(
            transform_frame, 
            textvariable=self.kf_y_var, 
            width=60
        ).pack(side="left", padx=2)
        
        # Scale and rotation
        ctk.CTkLabel(transform_frame, text="Scale:").pack(side="left", padx=5)
        self.kf_scale_var = ctk.DoubleVar(value=1.0)
        ctk.CTkEntry(
            transform_frame, 
            textvariable=self.kf_scale_var, 
            width=60
        ).pack(side="left", padx=2)
        
        ctk.CTkLabel(transform_frame, text="Rotation:").pack(side="left", padx=5)
        self.kf_rotation_var = ctk.DoubleVar()
        ctk.CTkEntry(
            transform_frame, 
            textvariable=self.kf_rotation_var, 
            width=60
        ).pack(side="left", padx=2)
        
        # Opacity
        ctk.CTkLabel(transform_frame, text="Opacity:").pack(side="left", padx=5)
        self.kf_opacity_var = ctk.DoubleVar(value=1.0)
        ctk.CTkEntry(
            transform_frame, 
            textvariable=self.kf_opacity_var, 
            width=60
        ).pack(side="left", padx=2)
        
        # Action buttons
        button_frame = ctk.CTkFrame(props_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="Delete Keyframe",
            command=self._delete_selected_keyframe,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Copy Keyframe",
            command=self._copy_selected_keyframe
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Reset Transform",
            command=self._reset_keyframe_transform
        ).pack(side="right", padx=5)
        
    def _draw_timeline(self):
        """Draw the timeline with tracks and keyframes."""
        self.timeline_canvas.delete("all")
        
        canvas_width = self.timeline_width * self.zoom_level
        
        # Update scroll region
        self.timeline_canvas.configure(scrollregion=(0, 0, canvas_width, self.timeline_height))
        
        # Draw time grid
        self._draw_time_grid(canvas_width)
        
        # Draw tracks
        self._draw_tracks()
        
        # Draw keyframes
        self._draw_keyframes(canvas_width)
        
        # Draw playhead
        self._draw_playhead(canvas_width)
        
    def _draw_time_grid(self, canvas_width: float):
        """Draw time grid lines and labels."""
        # Major grid lines (seconds)
        pixels_per_second = canvas_width / self.timeline_duration
        
        for i in range(int(self.timeline_duration) + 1):
            x = i * pixels_per_second
            self.timeline_canvas.create_line(
                x, 0, x, self.timeline_height,
                fill=self.grid_color,
                width=1
            )
            
            # Time labels
            self.timeline_canvas.create_text(
                x + 5, 15,
                text=f"{i}s",
                fill="white",
                anchor="w",
                font=("Arial", 9)
            )
        
        # Minor grid lines (0.1 second intervals)
        for i in range(int(self.timeline_duration * 10) + 1):
            x = i * pixels_per_second / 10
            if i % 10 != 0:  # Don't draw over major lines
                self.timeline_canvas.create_line(
                    x, 0, x, self.timeline_height,
                    fill=self.grid_color,
                    width=1,
                    stipple="gray25"
                )
    
    def _draw_tracks(self):
        """Draw animation tracks."""
        track_names = ["Position", "Scale", "Rotation", "Opacity", "Effects"]
        
        for i, track_name in enumerate(track_names):
            y = 40 + i * self.track_height
            
            # Track background
            self.timeline_canvas.create_rectangle(
                0, y, self.timeline_width * self.zoom_level, y + self.track_height - 2,
                fill=self.track_color,
                outline=self.grid_color
            )
            
            # Track label
            self.timeline_canvas.create_text(
                10, y + self.track_height // 2,
                text=track_name,
                fill="white",
                anchor="w",
                font=("Arial", 10, "bold")
            )
    
    def _draw_keyframes(self, canvas_width: float):
        """Draw keyframes on the timeline."""
        if not self.asset or not MEDIA_SYSTEM_AVAILABLE:
            return
        
        pixels_per_second = canvas_width / self.timeline_duration
        
        # Draw keyframes for each animation
        for anim_idx, animation in enumerate(self.asset.animations):
            keyframes = animation.get('keyframes', [])
            track_y = 40 + (anim_idx % 5) * self.track_height + self.track_height // 2
            
            for kf in keyframes:
                time = kf.get('time', 0)
                x = time * pixels_per_second
                
                # Keyframe diamond
                color = self.selected_keyframe_color if kf == self.selected_keyframe else self.keyframe_color
                
                self.timeline_canvas.create_oval(
                    x - self.keyframe_radius, track_y - self.keyframe_radius,
                    x + self.keyframe_radius, track_y + self.keyframe_radius,
                    fill=color,
                    outline="white",
                    width=2,
                    tags=f"keyframe_{id(kf)}"
                )
                
                # Store keyframe data for click detection
                self.timeline_canvas.tag_bind(
                    f"keyframe_{id(kf)}", 
                    "<Button-1>", 
                    lambda e, kf=kf: self._select_keyframe(kf)
                )
    
    def _draw_playhead(self, canvas_width: float):
        """Draw the playhead indicator."""
        pixels_per_second = canvas_width / self.timeline_duration
        x = self.playhead_position * pixels_per_second
        
        self.timeline_canvas.create_line(
            x, 0, x, self.timeline_height,
            fill=self.playhead_color,
            width=3,
            tags="playhead"
        )
        
        # Playhead handle
        self.timeline_canvas.create_polygon(
            x - 8, 0, x + 8, 0, x, 15,
            fill=self.playhead_color,
            outline="white",
            tags="playhead"
        )
    
    def _on_canvas_click(self, event):
        """Handle canvas click events."""
        canvas_x = self.timeline_canvas.canvasx(event.x)
        canvas_y = self.timeline_canvas.canvasy(event.y)
        
        # Convert to timeline time
        pixels_per_second = (self.timeline_width * self.zoom_level) / self.timeline_duration
        time = canvas_x / pixels_per_second
        
        # Check if clicking on playhead
        playhead_x = self.playhead_position * pixels_per_second
        if abs(canvas_x - playhead_x) < 10:
            self._set_playhead_position(time)
            return
        
        # Check if clicking on a keyframe
        clicked_items = self.timeline_canvas.find_overlapping(
            canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5
        )
        
        keyframe_clicked = False
        for item in clicked_items:
            tags = self.timeline_canvas.gettags(item)
            for tag in tags:
                if tag.startswith("keyframe_"):
                    keyframe_clicked = True
                    break
        
        if not keyframe_clicked:
            # Click on empty space - move playhead
            self._set_playhead_position(time)
            self._deselect_keyframe()
    
    def _on_canvas_drag(self, event):
        """Handle canvas drag events."""
        if self.dragging_keyframe:
            canvas_x = self.timeline_canvas.canvasx(event.x)
            pixels_per_second = (self.timeline_width * self.zoom_level) / self.timeline_duration
            new_time = max(0, min(self.timeline_duration, canvas_x / pixels_per_second))
            
            # Update keyframe time
            self.dragging_keyframe['time'] = new_time
            self._draw_timeline()
            self._update_keyframe_properties_ui()
    
    def _on_canvas_release(self, event):
        """Handle canvas release events."""
        if self.dragging_keyframe:
            self.dragging_keyframe = None
            if self.on_change_callback:
                self.on_change_callback()
    
    def _on_canvas_double_click(self, event):
        """Handle canvas double-click to add keyframe."""
        canvas_x = self.timeline_canvas.canvasx(event.x)
        pixels_per_second = (self.timeline_width * self.zoom_level) / self.timeline_duration
        time = canvas_x / pixels_per_second
        
        self._add_keyframe_at_time(time)
    
    def _select_keyframe(self, keyframe):
        """Select a keyframe and update properties UI."""
        self.selected_keyframe = keyframe
        self.dragging_keyframe = keyframe
        self._update_keyframe_properties_ui()
        self._draw_timeline()
    
    def _deselect_keyframe(self):
        """Deselect current keyframe."""
        self.selected_keyframe = None
        self.dragging_keyframe = None
        self._clear_keyframe_properties_ui()
        self._draw_timeline()
    
    def _update_keyframe_properties_ui(self):
        """Update the keyframe properties UI with selected keyframe data."""
        if not self.selected_keyframe:
            return
        
        # Update time
        self.keyframe_time_var.set(self.selected_keyframe.get('time', 0))
        
        # Update transform properties from keyframe properties
        props = self.selected_keyframe.get('properties', {})
        self.kf_x_var.set(props.get('x', 0))
        self.kf_y_var.set(props.get('y', 0))
        self.kf_scale_var.set(props.get('scale', 1.0))
        self.kf_rotation_var.set(props.get('rotation', 0))
        self.kf_opacity_var.set(props.get('opacity', 1.0))
    
    def _clear_keyframe_properties_ui(self):
        """Clear the keyframe properties UI."""
        self.keyframe_time_var.set(0)
        self.kf_x_var.set(0)
        self.kf_y_var.set(0)
        self.kf_scale_var.set(1.0)
        self.kf_rotation_var.set(0)
        self.kf_opacity_var.set(1.0)
    
    def _on_keyframe_property_change(self, event=None):
        """Handle keyframe property changes."""
        if not self.selected_keyframe:
            return
        
        # Update keyframe properties
        self.selected_keyframe['time'] = self.keyframe_time_var.get()
        
        if 'properties' not in self.selected_keyframe:
            self.selected_keyframe['properties'] = {}
        
        props = self.selected_keyframe['properties']
        props['x'] = self.kf_x_var.get()
        props['y'] = self.kf_y_var.get()
        props['scale'] = self.kf_scale_var.get()
        props['rotation'] = self.kf_rotation_var.get()
        props['opacity'] = self.kf_opacity_var.get()
        
        # Redraw timeline
        self._draw_timeline()
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def _set_playhead_position(self, time: float):
        """Set playhead position."""
        self.playhead_position = max(0, min(self.timeline_duration, time))
        self._draw_timeline()
    
    def _add_keyframe_at_playhead(self):
        """Add keyframe at current playhead position."""
        self._add_keyframe_at_time(self.playhead_position)
    
    def _add_keyframe_at_time(self, time: float):
        """Add a keyframe at the specified time."""
        if not self.asset:
            return
        
        # Create new keyframe
        keyframe = {
            'time': time,
            'properties': {
                'x': self.asset.x,
                'y': self.asset.y,
                'scale': 1.0,
                'rotation': self.asset.rotation,
                'opacity': self.asset.opacity
            },
            'easing': 'ease-in-out'
        }
        
        # Add to first animation or create new one
        if self.asset.animations:
            self.asset.animations[0].setdefault('keyframes', []).append(keyframe)
        else:
            animation = {
                'type': 'custom',
                'duration': self.timeline_duration,
                'keyframes': [keyframe]
            }
            self.asset.animations.append(animation)
        
        # Select the new keyframe
        self._select_keyframe(keyframe)
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def _delete_selected_keyframe(self):
        """Delete the selected keyframe."""
        if not self.selected_keyframe or not self.asset:
            return
        
        # Find and remove keyframe from animations
        for animation in self.asset.animations:
            keyframes = animation.get('keyframes', [])
            if self.selected_keyframe in keyframes:
                keyframes.remove(self.selected_keyframe)
                break
        
        self._deselect_keyframe()
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def _copy_selected_keyframe(self):
        """Copy the selected keyframe."""
        if not self.selected_keyframe:
            return
        
        # Create copy at playhead position
        new_keyframe = {
            'time': self.playhead_position,
            'properties': self.selected_keyframe['properties'].copy(),
            'easing': self.selected_keyframe.get('easing', 'ease-in-out')
        }
        
        # Add to same animation
        for animation in self.asset.animations:
            keyframes = animation.get('keyframes', [])
            if self.selected_keyframe in keyframes:
                keyframes.append(new_keyframe)
                break
        
        self._select_keyframe(new_keyframe)
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def _reset_keyframe_transform(self):
        """Reset keyframe transform to defaults."""
        if not self.selected_keyframe:
            return
        
        props = self.selected_keyframe.setdefault('properties', {})
        props['x'] = 0
        props['y'] = 0
        props['scale'] = 1.0
        props['rotation'] = 0
        props['opacity'] = 1.0
        
        self._update_keyframe_properties_ui()
        self._draw_timeline()
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def _on_duration_change(self, event=None):
        """Handle timeline duration change."""
        try:
            new_duration = self.duration_var.get()
            if new_duration > 0:
                self.timeline_duration = new_duration
                self._draw_timeline()
        except:
            pass
    
    def _on_zoom_change(self, value):
        """Handle zoom level change."""
        self.zoom_level = float(value)
        self._draw_timeline()
    
    def _go_to_start(self):
        """Go to timeline start."""
        self._set_playhead_position(0)
    
    def _play_pause(self):
        """Toggle play/pause (placeholder)."""
        messagebox.showinfo("Preview", "Timeline playback preview coming soon!")
    
    def _stop(self):
        """Stop playback."""
        self._set_playhead_position(0)
    
    def load_asset(self, asset: 'MediaAsset'):
        """Load an asset into the timeline editor."""
        self.asset = asset
        self.selected_keyframe = None
        self.dragging_keyframe = None
        self.playhead_position = 0
        
        # Update duration based on asset animations
        if asset and asset.animations:
            max_duration = 0
            for animation in asset.animations:
                duration = animation.get('duration', 0)
                keyframes = animation.get('keyframes', [])
                if keyframes:
                    max_time = max(kf.get('time', 0) for kf in keyframes)
                    max_duration = max(max_duration, max_time, duration)
            
            if max_duration > 0:
                self.timeline_duration = max_duration + 1
                self.duration_var.set(self.timeline_duration)
        
        self._draw_timeline()
        self._clear_keyframe_properties_ui()
    
    def clear(self):
        """Clear the timeline editor."""
        self.asset = None
        self.selected_keyframe = None
        self.dragging_keyframe = None
        self.playhead_position = 0
        self._draw_timeline()
        self._clear_keyframe_properties_ui()