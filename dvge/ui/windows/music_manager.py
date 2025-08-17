# dvge/ui/windows/music_manager.py

"""Music Manager Window for the Dynamic Music System."""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from ...constants import *
from ...models.music_system import DynamicMusicEngine, MusicTrack, MusicMood, MusicIntensity


class MusicManagerWindow(ctk.CTkToplevel):
    """Window for managing the dynamic music system."""
    
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.app = parent_app
        self.music_engine = getattr(parent_app, 'music_engine', DynamicMusicEngine())
        
        # Ensure the app has a music engine
        if not hasattr(parent_app, 'music_engine'):
            parent_app.music_engine = self.music_engine
        
        self.current_track = None
        
        self.title("Dynamic Music Manager")
        self.geometry("1200x800")
        self.transient(parent_app)
        self.resizable(True, True)
        
        # Make window modal
        self.grab_set()
        
        self._setup_ui()
        self._refresh_track_list()
        
        # Center the window
        self.center_window()
    
    def center_window(self):
        """Center the window on the parent."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_track_list()
        self._create_track_editor()
        self._create_button_bar()
    
    def _create_track_list(self):
        """Create the track list panel."""
        list_frame = ctk.CTkFrame(self, width=300)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        list_frame.grid_propagate(False)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Music Tracks",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add",
            width=60,
            command=self._add_track
        )
        add_btn.grid(row=0, column=1, padx=(5, 0))
        
        # Track list
        self.track_listbox = ctk.CTkScrollableFrame(list_frame)
        self.track_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Filter controls
        filter_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        filter_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkLabel(filter_frame, text="Filter by mood:").pack(anchor="w")
        self.mood_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All"] + [mood.value.title() for mood in MusicMood],
            command=self._filter_tracks
        )
        self.mood_filter.pack(fill="x", pady=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        import_btn = ctk.CTkButton(
            btn_frame,
            text="Import Folder",
            command=self._import_music_folder
        )
        import_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color="red",
            hover_color="darkred",
            command=self._delete_track
        )
        delete_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))
    
    def _create_track_editor(self):
        """Create the track editing panel."""
        editor_frame = ctk.CTkFrame(self)
        editor_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(editor_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header.grid_columnconfigure(1, weight=1)
        
        self.editor_title = ctk.CTkLabel(
            header,
            text="Select a track to edit",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.editor_title.grid(row=0, column=0, sticky="w")
        
        # Test music button
        self.test_btn = ctk.CTkButton(
            header,
            text="🎵 Test Track",
            width=100,
            command=self._test_track,
            state="disabled"
        )
        self.test_btn.grid(row=0, column=1, sticky="e")
        
        # Main content - use notebook for tabs
        self.notebook = ctk.CTkTabview(editor_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Create tabs
        self.basic_tab = self.notebook.add("Basic Settings")
        self.context_tab = self.notebook.add("Context & Mood")
        self.technical_tab = self.notebook.add("Technical")
        self.advanced_tab = self.notebook.add("Advanced")
        
        self._create_empty_editor()
    
    def _create_empty_editor(self):
        """Create empty state for editor."""
        # Clear existing content
        for tab in [self.basic_tab, self.context_tab, self.technical_tab, self.advanced_tab]:
            for widget in tab.winfo_children():
                widget.destroy()
        
        empty_label = ctk.CTkLabel(
            self.basic_tab,
            text="Select a track from the list to edit its properties",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        empty_label.pack(pady=50)
    
    def _create_track_editor_tabs(self, track: MusicTrack):
        """Create editor interface for a specific track."""
        # Clear existing content
        for tab in [self.basic_tab, self.context_tab, self.technical_tab, self.advanced_tab]:
            for widget in tab.winfo_children():
                widget.destroy()
        
        self._create_basic_tab(track)
        self._create_context_tab(track)
        self._create_technical_tab(track)
        self._create_advanced_tab(track)
    
    def _create_basic_tab(self, track: MusicTrack):
        """Create the basic settings tab."""
        scroll_frame = ctk.CTkScrollableFrame(self.basic_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Track Information
        info_frame = ctk.CTkFrame(scroll_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_frame, text="Track Information", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        # Name
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill="x", padx=15, pady=5)
        name_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(name_frame, text="Name:", width=100).grid(row=0, column=0, sticky="w")
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="Track name")
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self.name_entry.insert(0, track.name)
        self.name_entry.bind('<KeyRelease>', lambda e: self._update_track_name())
        
        # File path
        file_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=15, pady=5)
        file_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(file_frame, text="File:", width=100).grid(row=0, column=0, sticky="w")
        self.file_entry = ctk.CTkEntry(file_frame, placeholder_text="Audio file path")
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(10, 5))
        self.file_entry.insert(0, track.file_path)
        self.file_entry.bind('<KeyRelease>', lambda e: self._update_track_file())
        
        browse_btn = ctk.CTkButton(file_frame, text="Browse", width=70, command=self._browse_audio_file)
        browse_btn.grid(row=0, column=2)
        
        # Volume and Priority
        controls_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=15, pady=(5, 15))
        controls_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(controls_frame, text="Volume:", width=100).grid(row=0, column=0, sticky="w")
        self.volume_slider = ctk.CTkSlider(controls_frame, from_=0.0, to=1.0, number_of_steps=20)
        self.volume_slider.grid(row=0, column=1, sticky="ew", padx=(10, 20))
        self.volume_slider.set(track.volume)
        self.volume_slider.configure(command=self._update_volume)
        
        ctk.CTkLabel(controls_frame, text="Priority:", width=80).grid(row=0, column=2, sticky="w")
        self.priority_slider = ctk.CTkSlider(controls_frame, from_=1, to=10, number_of_steps=9)
        self.priority_slider.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        self.priority_slider.set(track.priority)
        self.priority_slider.configure(command=self._update_priority)
        
        # Mood and Intensity
        mood_frame = ctk.CTkFrame(scroll_frame)
        mood_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(mood_frame, text="Mood & Intensity", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        mood_controls = ctk.CTkFrame(mood_frame, fg_color="transparent")
        mood_controls.pack(fill="x", padx=15, pady=(0, 15))
        mood_controls.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(mood_controls, text="Mood:", width=100).grid(row=0, column=0, sticky="w")
        self.mood_menu = ctk.CTkOptionMenu(
            mood_controls,
            values=[mood.value.title() for mood in MusicMood],
            command=self._update_mood
        )
        self.mood_menu.grid(row=0, column=1, sticky="ew", padx=(10, 20))
        self.mood_menu.set(track.mood.value.title())
        
        ctk.CTkLabel(mood_controls, text="Intensity:", width=80).grid(row=0, column=2, sticky="w")
        self.intensity_menu = ctk.CTkOptionMenu(
            mood_controls,
            values=[f"{i.value} - {i.name.title()}" for i in MusicIntensity],
            command=self._update_intensity
        )
        self.intensity_menu.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        self.intensity_menu.set(f"{track.intensity.value} - {track.intensity.name.title()}")
    
    def _create_context_tab(self, track: MusicTrack):
        """Create the context and mood tab."""
        scroll_frame = ctk.CTkScrollableFrame(self.context_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Situations
        sit_frame = ctk.CTkFrame(scroll_frame)
        sit_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(sit_frame, text="Usage Situations", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        situations_grid = ctk.CTkFrame(sit_frame, fg_color="transparent")
        situations_grid.pack(fill="x", padx=15, pady=(0, 15))
        
        self.situation_vars = {}
        situations = ["dialogue", "combat", "exploration", "romance", "suspense", "victory", "defeat", "shop", "menu"]
        
        for i, situation in enumerate(situations):
            var = ctk.BooleanVar(value=situation in track.situations)
            checkbox = ctk.CTkCheckBox(
                situations_grid,
                text=situation.title(),
                variable=var,
                command=lambda s=situation: self._update_situations()
            )
            checkbox.grid(row=i//3, column=i%3, sticky="w", padx=10, pady=2)
            self.situation_vars[situation] = var
        
        # Emotions
        emotions_frame = ctk.CTkFrame(scroll_frame)
        emotions_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(emotions_frame, text="Emotional Context", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        self.emotions_entry = ctk.CTkEntry(
            emotions_frame,
            placeholder_text="Enter emotions (comma-separated): joy, fear, excitement"
        )
        self.emotions_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.emotions_entry.insert(0, ", ".join(track.emotions))
        self.emotions_entry.bind('<KeyRelease>', lambda e: self._update_emotions())
        
        # Characters
        chars_frame = ctk.CTkFrame(scroll_frame)
        chars_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(chars_frame, text="Associated Characters", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        self.characters_entry = ctk.CTkEntry(
            chars_frame,
            placeholder_text="Enter character names (comma-separated)"
        )
        self.characters_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.characters_entry.insert(0, ", ".join(track.characters))
        self.characters_entry.bind('<KeyRelease>', lambda e: self._update_characters())
        
        # Tags
        tags_frame = ctk.CTkFrame(scroll_frame)
        tags_frame.pack(fill="x")
        
        ctk.CTkLabel(tags_frame, text="Music Tags", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        self.tags_entry = ctk.CTkEntry(
            tags_frame,
            placeholder_text="Enter tags (comma-separated): orchestral, piano, electronic"
        )
        self.tags_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.tags_entry.insert(0, ", ".join(track.tags))
        self.tags_entry.bind('<KeyRelease>', lambda e: self._update_tags())
    
    def _create_technical_tab(self, track: MusicTrack):
        """Create the technical settings tab."""
        scroll_frame = ctk.CTkScrollableFrame(self.technical_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Audio Properties
        audio_frame = ctk.CTkFrame(scroll_frame)
        audio_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(audio_frame, text="Audio Properties", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        # Duration and BPM
        props_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        props_frame.pack(fill="x", padx=15, pady=5)
        props_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(props_frame, text="Duration (s):", width=100).grid(row=0, column=0, sticky="w")
        self.duration_entry = ctk.CTkEntry(props_frame, width=100)
        self.duration_entry.grid(row=0, column=1, sticky="w", padx=(10, 20))
        self.duration_entry.insert(0, str(track.duration))
        self.duration_entry.bind('<KeyRelease>', lambda e: self._update_duration())
        
        ctk.CTkLabel(props_frame, text="BPM:", width=50).grid(row=0, column=2, sticky="w")
        self.bpm_entry = ctk.CTkEntry(props_frame, width=100)
        self.bpm_entry.grid(row=0, column=3, sticky="w", padx=(10, 0))
        self.bpm_entry.insert(0, str(track.bpm))
        self.bpm_entry.bind('<KeyRelease>', lambda e: self._update_bpm())
        
        # Loop settings
        loop_frame = ctk.CTkFrame(audio_frame, fg_color="transparent")
        loop_frame.pack(fill="x", padx=15, pady=(5, 15))
        loop_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        self.is_loopable = ctk.BooleanVar(value=track.is_loopable)
        loop_checkbox = ctk.CTkCheckBox(
            loop_frame,
            text="Loopable",
            variable=self.is_loopable,
            command=self._update_loopable
        )
        loop_checkbox.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(loop_frame, text="Loop Start:", width=80).grid(row=0, column=1, sticky="w", padx=(20, 5))
        self.loop_start_entry = ctk.CTkEntry(loop_frame, width=80)
        self.loop_start_entry.grid(row=0, column=2, sticky="w", padx=(5, 20))
        self.loop_start_entry.insert(0, str(track.loop_start))
        self.loop_start_entry.bind('<KeyRelease>', lambda e: self._update_loop_start())
        
        ctk.CTkLabel(loop_frame, text="Loop End:", width=70).grid(row=0, column=3, sticky="w", padx=(0, 5))
        self.loop_end_entry = ctk.CTkEntry(loop_frame, width=80)
        self.loop_end_entry.grid(row=0, column=4, sticky="w", padx=5)
        self.loop_end_entry.insert(0, str(track.loop_end))
        self.loop_end_entry.bind('<KeyRelease>', lambda e: self._update_loop_end())
        
        # Fade settings
        fade_frame = ctk.CTkFrame(scroll_frame)
        fade_frame.pack(fill="x")
        
        ctk.CTkLabel(fade_frame, text="Transition Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        fade_controls = ctk.CTkFrame(fade_frame, fg_color="transparent")
        fade_controls.pack(fill="x", padx=15, pady=(0, 15))
        fade_controls.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(fade_controls, text="Fade In:", width=100).grid(row=0, column=0, sticky="w")
        self.fade_in_slider = ctk.CTkSlider(fade_controls, from_=0.0, to=10.0, number_of_steps=20)
        self.fade_in_slider.grid(row=0, column=1, sticky="ew", padx=(10, 20))
        self.fade_in_slider.set(track.fade_in_time)
        self.fade_in_slider.configure(command=self._update_fade_in)
        
        ctk.CTkLabel(fade_controls, text="Fade Out:", width=100).grid(row=0, column=2, sticky="w")
        self.fade_out_slider = ctk.CTkSlider(fade_controls, from_=0.0, to=10.0, number_of_steps=20)
        self.fade_out_slider.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        self.fade_out_slider.set(track.fade_out_time)
        self.fade_out_slider.configure(command=self._update_fade_out)
    
    def _create_advanced_tab(self, track: MusicTrack):
        """Create the advanced settings tab."""
        scroll_frame = ctk.CTkScrollableFrame(self.advanced_tab)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Auto-selection conditions
        conditions_frame = ctk.CTkFrame(scroll_frame)
        conditions_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(conditions_frame, text="Auto-Selection Rules", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        info_label = ctk.CTkLabel(
            conditions_frame,
            text="Define when this track should automatically play (JSON format)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(padx=15, pady=(0, 5), anchor="w")
        
        self.conditions_text = ctk.CTkTextbox(conditions_frame, height=100)
        self.conditions_text.pack(fill="x", padx=15, pady=(0, 15))
        self.conditions_text.insert("0.0", str(track.play_conditions))
        
        # Advanced features placeholder
        advanced_frame = ctk.CTkFrame(scroll_frame)
        advanced_frame.pack(fill="x")
        
        ctk.CTkLabel(advanced_frame, text="Advanced Features", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 5), padx=15, anchor="w")
        
        info_label = ctk.CTkLabel(
            advanced_frame,
            text="Layers, variations, and stem tracks can be configured here in future updates.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(padx=15, pady=(0, 15), anchor="w")
    
    def _create_button_bar(self):
        """Create the bottom button bar."""
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Music engine settings
        settings_btn = ctk.CTkButton(
            button_frame,
            text="Engine Settings",
            command=self._open_engine_settings
        )
        settings_btn.grid(row=0, column=0, padx=15, pady=15)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy
        )
        close_btn.grid(row=0, column=2, padx=15, pady=15)
    
    def _refresh_track_list(self):
        """Refresh the track list display."""
        # Clear existing list
        for widget in self.track_listbox.winfo_children():
            widget.destroy()
        
        tracks = list(self.music_engine.tracks.values())
        
        # Apply mood filter
        selected_mood = self.mood_filter.get() if hasattr(self, 'mood_filter') else "All"
        if selected_mood != "All":
            tracks = [t for t in tracks if t.mood.value.title() == selected_mood]
        
        if not tracks:
            no_tracks_label = ctk.CTkLabel(
                self.track_listbox,
                text="No tracks yet.\nClick 'Add' to create one.",
                text_color="gray"
            )
            no_tracks_label.pack(pady=20)
            return
        
        for track in tracks:
            track_frame = ctk.CTkFrame(self.track_listbox)
            track_frame.pack(fill="x", pady=2)
            track_frame.grid_columnconfigure(0, weight=1)
            
            # Track info
            info_text = f"{track.name}\n{track.mood.value.title()} • Intensity {track.intensity.value}"
            if track.file_path:
                filename = os.path.basename(track.file_path)
                info_text += f"\n📁 {filename}"
            
            track_btn = ctk.CTkButton(
                track_frame,
                text=info_text,
                height=60,
                anchor="w",
                command=lambda t=track: self._select_track(t)
            )
            track_btn.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    
    def _select_track(self, track: MusicTrack):
        """Select a track for editing."""
        self.current_track = track
        self.editor_title.configure(text=f"Editing: {track.name}")
        self.test_btn.configure(state="normal")
        self._create_track_editor_tabs(track)
    
    def _add_track(self):
        """Add a new track."""
        dialog = ctk.CTkInputDialog(
            text="Enter track name:",
            title="Add Music Track"
        )
        name = dialog.get_input()
        
        if name:
            track_id = name.lower().replace(' ', '_').replace('-', '_')
            # Ensure unique ID
            counter = 1
            original_id = track_id
            while self.music_engine.get_track(track_id):
                track_id = f"{original_id}_{counter}"
                counter += 1
            
            track = MusicTrack(track_id, name)
            self.music_engine.add_track(track)
            self._refresh_track_list()
            self._select_track(track)
    
    def _delete_track(self):
        """Delete the selected track."""
        if not self.current_track:
            messagebox.showwarning("No Selection", "Please select a track to delete.")
            return
        
        result = messagebox.askyesno(
            "Delete Track",
            f"Are you sure you want to delete '{self.current_track.name}'?"
        )
        
        if result:
            self.music_engine.remove_track(self.current_track.track_id)
            self.current_track = None
            self._refresh_track_list()
            self._create_empty_editor()
            self.editor_title.configure(text="Select a track to edit")
            self.test_btn.configure(state="disabled")
    
    def _import_music_folder(self):
        """Import music tracks from a folder."""
        folder_path = filedialog.askdirectory(
            title="Select folder containing music files"
        )
        
        if folder_path:
            try:
                imported_count = 0
                audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac']
                
                for filename in os.listdir(folder_path):
                    if any(filename.lower().endswith(ext) for ext in audio_extensions):
                        file_path = os.path.join(folder_path, filename)
                        track_name = os.path.splitext(filename)[0]
                        track_id = track_name.lower().replace(' ', '_').replace('-', '_')
                        
                        # Ensure unique ID
                        counter = 1
                        original_id = track_id
                        while self.music_engine.get_track(track_id):
                            track_id = f"{original_id}_{counter}"
                            counter += 1
                        
                        track = MusicTrack(track_id, track_name, file_path)
                        
                        # Try to auto-detect mood from filename
                        filename_lower = filename.lower()
                        if any(word in filename_lower for word in ['combat', 'battle', 'fight']):
                            track.mood = MusicMood.COMBAT
                            track.intensity = MusicIntensity.HIGH
                        elif any(word in filename_lower for word in ['peaceful', 'calm', 'ambient']):
                            track.mood = MusicMood.PEACEFUL
                            track.intensity = MusicIntensity.LOW
                        elif any(word in filename_lower for word in ['romantic', 'love']):
                            track.mood = MusicMood.ROMANTIC
                            track.intensity = MusicIntensity.MEDIUM
                        elif any(word in filename_lower for word in ['sad', 'melancholy']):
                            track.mood = MusicMood.SAD
                            track.intensity = MusicIntensity.LOW
                        elif any(word in filename_lower for word in ['epic', 'heroic', 'triumph']):
                            track.mood = MusicMood.EPIC
                            track.intensity = MusicIntensity.INTENSE
                        
                        self.music_engine.add_track(track)
                        imported_count += 1
                
                self._refresh_track_list()
                messagebox.showinfo(
                    "Import Complete",
                    f"Imported {imported_count} music tracks."
                )
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import tracks: {str(e)}")
    
    def _filter_tracks(self, selected_mood):
        """Filter tracks by mood."""
        self._refresh_track_list()
    
    def _test_track(self):
        """Test play the selected track."""
        if self.current_track:
            messagebox.showinfo(
                "Test Track",
                f"Testing track: {self.current_track.name}\n\n"
                f"In a real implementation, this would play:\n{self.current_track.file_path}\n\n"
                f"Mood: {self.current_track.mood.value.title()}\n"
                f"Intensity: {self.current_track.intensity.value}"
            )
    
    def _browse_audio_file(self):
        """Browse for an audio file."""
        if not self.current_track:
            return
        
        file_path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[
                ("Audio files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
                ("MP3 files", "*.mp3"),
                ("WAV files", "*.wav"),
                ("OGG files", "*.ogg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.current_track.file_path = file_path
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)
            self._refresh_track_list()
    
    def _open_engine_settings(self):
        """Open music engine settings dialog."""
        messagebox.showinfo(
            "Engine Settings",
            "Music Engine Settings:\n\n"
            f"Auto-selection: {'Enabled' if self.music_engine.enable_auto_selection else 'Disabled'}\n"
            f"Transition: {self.music_engine.default_transition.value.title()}\n"
            f"Transition Duration: {self.music_engine.transition_duration}s\n\n"
            "Advanced settings will be available in future updates."
        )
    
    # Update methods for track properties
    def _update_track_name(self):
        if self.current_track:
            self.current_track.name = self.name_entry.get()
            self._refresh_track_list()
    
    def _update_track_file(self):
        if self.current_track:
            self.current_track.file_path = self.file_entry.get()
    
    def _update_volume(self, value):
        if self.current_track:
            self.current_track.volume = value
    
    def _update_priority(self, value):
        if self.current_track:
            self.current_track.priority = int(value)
    
    def _update_mood(self, value):
        if self.current_track:
            mood_name = value.lower()
            for mood in MusicMood:
                if mood.value == mood_name:
                    self.current_track.mood = mood
                    break
            self._refresh_track_list()
    
    def _update_intensity(self, value):
        if self.current_track:
            intensity_value = int(value.split(' - ')[0])
            for intensity in MusicIntensity:
                if intensity.value == intensity_value:
                    self.current_track.intensity = intensity
                    break
            self._refresh_track_list()
    
    def _update_situations(self):
        if self.current_track:
            self.current_track.situations = [
                situation for situation, var in self.situation_vars.items() 
                if var.get()
            ]
    
    def _update_emotions(self):
        if self.current_track:
            emotions_text = self.emotions_entry.get().strip()
            self.current_track.emotions = [
                emotion.strip() for emotion in emotions_text.split(',')
                if emotion.strip()
            ]
    
    def _update_characters(self):
        if self.current_track:
            chars_text = self.characters_entry.get().strip()
            self.current_track.characters = [
                char.strip() for char in chars_text.split(',')
                if char.strip()
            ]
    
    def _update_tags(self):
        if self.current_track:
            tags_text = self.tags_entry.get().strip()
            self.current_track.tags = [
                tag.strip() for tag in tags_text.split(',')
                if tag.strip()
            ]
    
    def _update_duration(self):
        if self.current_track:
            try:
                self.current_track.duration = float(self.duration_entry.get() or 0)
            except ValueError:
                pass
    
    def _update_bpm(self):
        if self.current_track:
            try:
                self.current_track.bpm = int(self.bpm_entry.get() or 120)
            except ValueError:
                pass
    
    def _update_loopable(self):
        if self.current_track:
            self.current_track.is_loopable = self.is_loopable.get()
    
    def _update_loop_start(self):
        if self.current_track:
            try:
                self.current_track.loop_start = float(self.loop_start_entry.get() or 0)
            except ValueError:
                pass
    
    def _update_loop_end(self):
        if self.current_track:
            try:
                self.current_track.loop_end = float(self.loop_end_entry.get() or 0)
            except ValueError:
                pass
    
    def _update_fade_in(self, value):
        if self.current_track:
            self.current_track.fade_in_time = value
    
    def _update_fade_out(self, value):
        if self.current_track:
            self.current_track.fade_out_time = value