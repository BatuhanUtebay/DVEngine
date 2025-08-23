# dvge/ui/panels/voice_panel.py

"""Voice Acting Pipeline UI Panel."""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, List, Optional, Any
from ...constants import *
from ...features.voice_system import VoiceProfile, VoiceAsset


class VoicePanel(ctk.CTkFrame):
    """UI panel for voice acting pipeline management."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_SECONDARY_FRAME)
        self.app = app
        
        # Initialize voice manager if not already done
        if not hasattr(app, 'voice_manager'):
            from ...features.voice_system import VoiceManager
            app.voice_manager = VoiceManager(app)
        
        self.voice_manager = app.voice_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Voice assets list gets most space
        
        self._create_header()
        self._create_voice_profiles_section()
        self._create_voice_assets_section()
        self._create_character_assignments_section()
        self._create_controls_section()
        
        self._refresh_all()
    
    def _create_header(self):
        """Create the panel header."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header, 
            text="🎤 Voice Acting Pipeline", 
            font=FONT_SUBTITLE
        ).pack(side="left")
        
        # TTS Provider status
        self.provider_label = ctk.CTkLabel(
            header, 
            text="No TTS providers configured", 
            font=FONT_SMALL
        )
        self.provider_label.pack(side="right")
    
    def _create_voice_profiles_section(self):
        """Create voice profiles management section."""
        profiles_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        profiles_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        profiles_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            profiles_frame, 
            text="Voice Profiles:", 
            font=FONT_SUBTITLE_SMALL
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Voice profile dropdown
        self.voice_profile_var = ctk.StringVar(value="Select a voice profile...")
        self.voice_profile_dropdown = ctk.CTkOptionMenu(
            profiles_frame,
            variable=self.voice_profile_var,
            values=["No profiles available"],
            command=self._on_voice_profile_selected
        )
        self.voice_profile_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=(10, 5))
        
        # Profile management buttons
        button_frame = ctk.CTkFrame(profiles_frame, fg_color="transparent")
        button_frame.grid(row=0, column=2, padx=(5, 10), pady=(10, 5))
        
        ctk.CTkButton(
            button_frame,
            text="New",
            width=60,
            command=self._create_voice_profile
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            button_frame,
            text="Edit",
            width=60,
            command=self._edit_voice_profile
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            button_frame,
            text="Delete",
            width=60,
            fg_color=COLOR_DANGER,
            hover_color="#C0392B",
            command=self._delete_voice_profile
        ).pack(side="left")
        
        # Profile info section
        self.profile_info_frame = ctk.CTkFrame(profiles_frame, fg_color=COLOR_BACKGROUND)
        self.profile_info_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(5, 10))
        
        self.profile_info_label = ctk.CTkLabel(
            self.profile_info_frame,
            text="Select a voice profile to view details",
            font=FONT_SMALL,
            justify="left"
        )
        self.profile_info_label.pack(padx=10, pady=10)
    
    def _create_voice_assets_section(self):
        """Create voice assets management section."""
        assets_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        assets_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        assets_frame.grid_columnconfigure(0, weight=1)
        assets_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(assets_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header, 
            text="Voice Assets:", 
            font=FONT_SUBTITLE_SMALL
        ).pack(side="left")
        
        # Asset controls
        controls = ctk.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right")
        
        ctk.CTkButton(
            controls,
            text="Generate All",
            width=100,
            command=self._batch_generate_voices
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            controls,
            text="Play Selected",
            width=100,
            command=self._play_selected_asset
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            controls,
            text="Delete",
            width=80,
            fg_color=COLOR_DANGER,
            hover_color="#C0392B",
            command=self._delete_selected_asset
        ).pack(side="left")
        
        # Assets list
        self.assets_list = ctk.CTkScrollableFrame(assets_frame, fg_color=COLOR_BACKGROUND)
        self.assets_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.assets_list.grid_columnconfigure(0, weight=1)
        
        self.asset_widgets = {}  # Track asset widgets for selection
    
    def _create_character_assignments_section(self):
        """Create character voice assignments section."""
        assignments_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        assignments_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        assignments_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            assignments_frame, 
            text="Character Assignments:", 
            font=FONT_SUBTITLE_SMALL
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Character dropdown
        self.character_var = ctk.StringVar(value="Select character...")
        self.character_dropdown = ctk.CTkOptionMenu(
            assignments_frame,
            variable=self.character_var,
            values=["No characters available"],
            command=self._on_character_selected
        )
        self.character_dropdown.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=(10, 5))
        
        # Assign voice dropdown
        self.assign_voice_var = ctk.StringVar(value="Select voice...")
        self.assign_voice_dropdown = ctk.CTkOptionMenu(
            assignments_frame,
            variable=self.assign_voice_var,
            values=["No profiles available"]
        )
        self.assign_voice_dropdown.grid(row=0, column=2, sticky="ew", padx=(5, 5), pady=(10, 5))
        
        ctk.CTkButton(
            assignments_frame,
            text="Assign",
            width=80,
            command=self._assign_voice_to_character
        ).grid(row=0, column=3, padx=(5, 10), pady=(10, 5))
        
        # Current assignments display
        self.assignments_display = ctk.CTkTextbox(
            assignments_frame,
            height=60,
            font=FONT_SMALL
        )
        self.assignments_display.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=(5, 10))
    
    def _create_controls_section(self):
        """Create bottom controls section."""
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        ctk.CTkButton(
            controls_frame,
            text="Configure TTS Providers",
            command=self._open_tts_config
        ).pack(side="left")
        
        ctk.CTkButton(
            controls_frame,
            text="Export Voice Data",
            command=self._export_voice_data
        ).pack(side="left", padx=(10, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            controls_frame,
            text="Ready",
            font=FONT_SMALL
        )
        self.status_label.pack(side="right")
    
    def _refresh_all(self):
        """Refresh all UI elements."""
        self._refresh_voice_profiles()
        self._refresh_voice_assets()
        self._refresh_character_assignments()
        self._refresh_tts_status()
    
    def _refresh_voice_profiles(self):
        """Refresh voice profiles dropdown."""
        profiles = list(self.voice_manager.voice_profiles.keys())
        
        if profiles:
            profile_names = [
                f"{profile.name} ({profile.provider})" 
                for profile in self.voice_manager.voice_profiles.values()
            ]
            self.voice_profile_dropdown.configure(values=profile_names)
            
            # Update assign voice dropdown too
            self.assign_voice_dropdown.configure(values=profile_names)
        else:
            self.voice_profile_dropdown.configure(values=["No profiles available"])
            self.assign_voice_dropdown.configure(values=["No profiles available"])
    
    def _refresh_voice_assets(self):
        """Refresh voice assets list."""
        # Clear existing widgets
        for widget in self.assets_list.winfo_children():
            widget.destroy()
        
        self.asset_widgets.clear()
        
        assets = list(self.voice_manager.voice_assets.values())
        
        if not assets:
            no_assets_label = ctk.CTkLabel(
                self.assets_list,
                text="No voice assets generated yet",
                font=FONT_SMALL
            )
            no_assets_label.grid(row=0, column=0, pady=20)
            return
        
        # Sort assets by creation time (newest first)
        assets.sort(key=lambda x: x.created_timestamp, reverse=True)
        
        for i, asset in enumerate(assets):
            asset_frame = ctk.CTkFrame(self.assets_list, fg_color=COLOR_SECONDARY_FRAME)
            asset_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            asset_frame.grid_columnconfigure(1, weight=1)
            
            # Selection checkbox
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                asset_frame,
                text="",
                variable=var,
                width=20
            )
            checkbox.grid(row=0, column=0, padx=(10, 5), pady=10)
            
            # Asset info
            profile = self.voice_manager.get_voice_profile(asset.voice_profile_id)
            profile_name = profile.name if profile else "Unknown"
            
            info_text = f"{asset.text[:50]}{'...' if len(asset.text) > 50 else ''}"
            if asset.character_id:
                info_text += f" | Character: {asset.character_id}"
            info_text += f" | Voice: {profile_name}"
            
            info_label = ctk.CTkLabel(
                asset_frame,
                text=info_text,
                font=FONT_SMALL,
                anchor="w"
            )
            info_label.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
            
            # Duration and size
            duration_text = f"{asset.duration:.1f}s" if asset.duration > 0 else "Unknown"
            size_text = f"{asset.file_size // 1024}KB" if asset.file_size > 0 else "Unknown"
            
            stats_label = ctk.CTkLabel(
                asset_frame,
                text=f"{duration_text} | {size_text}",
                font=FONT_SMALL
            )
            stats_label.grid(row=0, column=2, padx=(5, 10), pady=10)
            
            self.asset_widgets[asset.id] = {
                'frame': asset_frame,
                'checkbox': checkbox,
                'var': var,
                'asset': asset
            }
    
    def _refresh_character_assignments(self):
        """Refresh character assignments display."""
        # Get characters from project (this is a simplified approach)
        characters = set()
        
        if hasattr(self.app, 'nodes'):
            for node in self.app.nodes.values():
                if hasattr(node, 'character') and node.character:
                    characters.add(node.character)
        
        character_list = list(characters)
        if character_list:
            self.character_dropdown.configure(values=character_list)
        else:
            self.character_dropdown.configure(values=["No characters found"])
        
        # Update assignments display
        assignments_text = ""
        for char_id, voice_id in self.voice_manager.character_voice_assignments.items():
            profile = self.voice_manager.get_voice_profile(voice_id)
            profile_name = profile.name if profile else "Unknown"
            assignments_text += f"{char_id} → {profile_name}\\n"
        
        if not assignments_text:
            assignments_text = "No character voice assignments yet"
        
        self.assignments_display.delete("1.0", tk.END)
        self.assignments_display.insert("1.0", assignments_text)
    
    def _refresh_tts_status(self):
        """Refresh TTS provider status."""
        if self.voice_manager.tts_manager:
            providers = self.voice_manager.get_available_providers()
            if providers:
                self.provider_label.configure(
                    text=f"TTS Providers: {', '.join(providers)}"
                )
            else:
                self.provider_label.configure(text="No TTS providers configured")
        else:
            self.provider_label.configure(text="TTS system unavailable")
    
    def _on_voice_profile_selected(self, selection):
        """Handle voice profile selection."""
        # Find the selected profile
        for profile in self.voice_manager.voice_profiles.values():
            if f"{profile.name} ({profile.provider})" == selection:
                self._display_profile_info(profile)
                break
    
    def _display_profile_info(self, profile: VoiceProfile):
        """Display detailed information about a voice profile."""
        info_text = f"""Name: {profile.name}
Provider: {profile.provider.upper()}
Voice ID: {profile.voice_id}
Language: {profile.language}
Gender: {profile.gender}
Style: {profile.style}
Speed: {profile.speed}x
Usage: {profile.usage_count} times
Description: {profile.description or 'None'}"""
        
        self.profile_info_label.configure(text=info_text, justify="left")
    
    def _on_character_selected(self, selection):
        """Handle character selection."""
        # Check if this character already has a voice assigned
        if selection in self.voice_manager.character_voice_assignments:
            voice_id = self.voice_manager.character_voice_assignments[selection]
            profile = self.voice_manager.get_voice_profile(voice_id)
            if profile:
                self.assign_voice_var.set(f"{profile.name} ({profile.provider})")
    
    def _create_voice_profile(self):
        """Open voice profile creation dialog."""
        VoiceProfileDialog(self, self.voice_manager, mode="create")
        self._refresh_voice_profiles()
    
    def _edit_voice_profile(self):
        """Edit selected voice profile."""
        selection = self.voice_profile_var.get()
        if selection == "Select a voice profile..." or selection == "No profiles available":
            messagebox.showwarning("No Selection", "Please select a voice profile to edit.")
            return
        
        # Find the selected profile
        for profile in self.voice_manager.voice_profiles.values():
            if f"{profile.name} ({profile.provider})" == selection:
                VoiceProfileDialog(self, self.voice_manager, mode="edit", profile=profile)
                self._refresh_voice_profiles()
                break
    
    def _delete_voice_profile(self):
        """Delete selected voice profile."""
        selection = self.voice_profile_var.get()
        if selection == "Select a voice profile..." or selection == "No profiles available":
            messagebox.showwarning("No Selection", "Please select a voice profile to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete voice profile '{selection}'?\\n\\n"
                              "This will also delete all associated voice assets."):
            
            # Find and delete the profile
            for profile in self.voice_manager.voice_profiles.values():
                if f"{profile.name} ({profile.provider})" == selection:
                    self.voice_manager.delete_voice_profile(profile.id)
                    self._refresh_all()
                    break
    
    def _assign_voice_to_character(self):
        """Assign selected voice to selected character."""
        character = self.character_var.get()
        voice_selection = self.assign_voice_var.get()
        
        if character == "Select character..." or character == "No characters found":
            messagebox.showwarning("No Character", "Please select a character.")
            return
        
        if voice_selection == "Select voice..." or voice_selection == "No profiles available":
            messagebox.showwarning("No Voice", "Please select a voice profile.")
            return
        
        # Find the voice profile ID
        for profile in self.voice_manager.voice_profiles.values():
            if f"{profile.name} ({profile.provider})" == voice_selection:
                success = self.voice_manager.assign_voice_to_character(character, profile.id)
                if success:
                    self._refresh_character_assignments()
                    self.status_label.configure(text=f"Assigned {profile.name} to {character}")
                else:
                    messagebox.showerror("Assignment Failed", "Failed to assign voice to character.")
                break
    
    def _batch_generate_voices(self):
        """Generate voices for all dialogue in the project."""
        if not self.voice_manager.character_voice_assignments:
            messagebox.showwarning("No Assignments", 
                                 "Please assign voices to characters first.")
            return
        
        # Show progress dialog
        progress_dialog = ProgressDialog(self, "Generating Voice Assets")
        
        def progress_callback(current, total):
            progress = int((current / total) * 100)
            progress_dialog.update_progress(progress, f"Processing {current}/{total} nodes...")
        
        try:
            results = self.voice_manager.batch_generate_for_project(progress_callback)
            progress_dialog.destroy()
            
            if results["success"]:
                messagebox.showinfo("Generation Complete", 
                                  f"Generated: {results['generated']}\\n"
                                  f"Skipped: {results['skipped']}\\n"
                                  f"Errors: {results['errors']}")
                self._refresh_voice_assets()
            else:
                messagebox.showerror("Generation Failed", results.get("error", "Unknown error"))
                
        except Exception as e:
            progress_dialog.destroy()
            messagebox.showerror("Generation Error", f"Error generating voices: {str(e)}")
    
    def _play_selected_asset(self):
        """Play the selected voice asset."""
        selected_assets = [
            data['asset'] for data in self.asset_widgets.values()
            if data['var'].get()
        ]
        
        if not selected_assets:
            messagebox.showwarning("No Selection", "Please select a voice asset to play.")
            return
        
        # Play the first selected asset
        asset = selected_assets[0]
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(asset.file_path)
            pygame.mixer.music.play()
            self.status_label.configure(text="Playing voice asset...")
        except ImportError:
            messagebox.showinfo("Playback Unavailable", 
                               f"Audio playback requires pygame.\\n\\nAsset location: {asset.file_path}")
        except Exception as e:
            messagebox.showerror("Playback Error", f"Error playing audio: {str(e)}")
    
    def _delete_selected_asset(self):
        """Delete selected voice assets."""
        selected_assets = [
            (data['asset'].id, data['asset'].text[:30])
            for data in self.asset_widgets.values()
            if data['var'].get()
        ]
        
        if not selected_assets:
            messagebox.showwarning("No Selection", "Please select voice assets to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete {len(selected_assets)} voice asset(s)?"):
            
            for asset_id, _ in selected_assets:
                self.voice_manager.delete_voice_asset(asset_id)
            
            self._refresh_voice_assets()
            self.status_label.configure(text=f"Deleted {len(selected_assets)} voice assets")
    
    def _open_tts_config(self):
        """Open TTS provider configuration dialog."""
        TTSConfigDialog(self, self.voice_manager.tts_manager)
        self._refresh_tts_status()
    
    def _export_voice_data(self):
        """Export voice data for external use."""
        file_path = filedialog.asksaveasfilename(
            title="Export Voice Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                import json
                voice_data = self.voice_manager.export_voice_data_for_html()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(voice_data, f, indent=2)
                
                messagebox.showinfo("Export Complete", f"Voice data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting voice data: {str(e)}")


class VoiceProfileDialog(ctk.CTkToplevel):
    """Dialog for creating/editing voice profiles."""
    
    def __init__(self, parent, voice_manager, mode="create", profile=None):
        super().__init__(parent)
        self.voice_manager = voice_manager
        self.mode = mode
        self.profile = profile
        
        self.title(f"{'Create' if mode == 'create' else 'Edit'} Voice Profile")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        
        if mode == "edit" and profile:
            self._populate_fields(profile)
    
    def _create_ui(self):
        """Create the dialog UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Name
        ctk.CTkLabel(main_frame, text="Name:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.name_entry = ctk.CTkEntry(main_frame)
        self.name_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Provider
        ctk.CTkLabel(main_frame, text="Provider:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        providers = self.voice_manager.get_available_providers()
        if not providers:
            providers = ["mock"]  # Always have mock for testing
        
        self.provider_var = ctk.StringVar(value=providers[0])
        self.provider_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.provider_var,
            values=providers,
            command=self._on_provider_changed
        )
        self.provider_dropdown.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Voice ID
        ctk.CTkLabel(main_frame, text="Voice:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.voice_id_var = ctk.StringVar(value="Select voice...")
        self.voice_id_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.voice_id_var,
            values=["Loading..."]
        )
        self.voice_id_dropdown.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Language
        ctk.CTkLabel(main_frame, text="Language:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.language_var = ctk.StringVar(value="en-US")
        self.language_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.language_var,
            values=["en-US", "en-GB", "en-AU", "en-CA"]
        )
        self.language_dropdown.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Gender
        ctk.CTkLabel(main_frame, text="Gender:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.gender_var = ctk.StringVar(value="neutral")
        self.gender_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.gender_var,
            values=["male", "female", "neutral"]
        )
        self.gender_dropdown.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Age Range
        ctk.CTkLabel(main_frame, text="Age Range:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.age_var = ctk.StringVar(value="adult")
        self.age_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.age_var,
            values=["child", "teen", "adult", "elderly"]
        )
        self.age_dropdown.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Style
        ctk.CTkLabel(main_frame, text="Style:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.style_var = ctk.StringVar(value="neutral")
        self.style_dropdown = ctk.CTkOptionMenu(
            main_frame,
            variable=self.style_var,
            values=["neutral", "cheerful", "sad", "angry", "excited", "calm", "dramatic"]
        )
        self.style_dropdown.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Speed
        ctk.CTkLabel(main_frame, text="Speed:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.speed_var = ctk.DoubleVar(value=1.0)
        self.speed_slider = ctk.CTkSlider(main_frame, from_=0.5, to=2.0, variable=self.speed_var)
        self.speed_slider.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        self.speed_label = ctk.CTkLabel(main_frame, text="1.0x")
        self.speed_label.grid(row=row, column=2, padx=5, pady=5)
        self.speed_slider.configure(command=self._update_speed_label)
        row += 1
        
        # Pitch
        ctk.CTkLabel(main_frame, text="Pitch:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.pitch_var = ctk.DoubleVar(value=1.0)
        self.pitch_slider = ctk.CTkSlider(main_frame, from_=0.5, to=2.0, variable=self.pitch_var)
        self.pitch_slider.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        self.pitch_label = ctk.CTkLabel(main_frame, text="1.0x")
        self.pitch_label.grid(row=row, column=2, padx=5, pady=5)
        self.pitch_slider.configure(command=self._update_pitch_label)
        row += 1
        
        # Volume
        ctk.CTkLabel(main_frame, text="Volume:").grid(row=row, column=0, sticky="w", padx=10, pady=5)
        self.volume_var = ctk.DoubleVar(value=1.0)
        self.volume_slider = ctk.CTkSlider(main_frame, from_=0.1, to=2.0, variable=self.volume_var)
        self.volume_slider.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        self.volume_label = ctk.CTkLabel(main_frame, text="1.0x")
        self.volume_label.grid(row=row, column=2, padx=5, pady=5)
        self.volume_slider.configure(command=self._update_volume_label)
        row += 1
        
        # Description
        ctk.CTkLabel(main_frame, text="Description:").grid(row=row, column=0, sticky="nw", padx=10, pady=5)
        self.description_text = ctk.CTkTextbox(main_frame, height=60)
        self.description_text.grid(row=row, column=1, columnspan=2, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Test Voice",
            command=self._test_voice
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_profile
        ).pack(side="right")
        
        # Load voices for initial provider
        self._on_provider_changed(self.provider_var.get())
    
    def _on_provider_changed(self, provider_name):
        """Handle provider selection change."""
        if self.voice_manager.tts_manager:
            provider = self.voice_manager.tts_manager.get_provider(provider_name)
            if provider and provider.is_configured:
                voices = provider.get_available_voices()
                voice_names = [f"{voice['name']} ({voice['id']})" for voice in voices]
                self.voice_id_dropdown.configure(values=voice_names)
                if voice_names:
                    self.voice_id_var.set(voice_names[0])
            else:
                self.voice_id_dropdown.configure(values=["Provider not configured"])
                self.voice_id_var.set("Provider not configured")
    
    def _update_speed_label(self, value):
        """Update speed label."""
        self.speed_label.configure(text=f"{value:.1f}x")
    
    def _update_pitch_label(self, value):
        """Update pitch label."""
        self.pitch_label.configure(text=f"{value:.1f}x")
    
    def _update_volume_label(self, value):
        """Update volume label."""
        self.volume_label.configure(text=f"{value:.1f}x")
    
    def _populate_fields(self, profile):
        """Populate fields with existing profile data."""
        self.name_entry.insert(0, profile.name)
        self.provider_var.set(profile.provider)
        self.language_var.set(profile.language)
        self.gender_var.set(profile.gender)
        self.age_var.set(profile.age_range)
        self.style_var.set(profile.style)
        self.speed_var.set(profile.speed)
        self.pitch_var.set(profile.pitch)
        self.volume_var.set(profile.volume)
        self.description_text.insert("1.0", profile.description)
        
        # Load voices and set selection
        self._on_provider_changed(profile.provider)
        self.voice_id_var.set(profile.voice_id)
    
    def _test_voice(self):
        """Test the current voice configuration."""
        test_text = "Hello! This is a test of the voice configuration."
        
        # Create temporary profile
        import uuid
        temp_profile = VoiceProfile(
            id=str(uuid.uuid4()),
            name="Test",
            provider=self.provider_var.get(),
            voice_id=self._extract_voice_id(self.voice_id_var.get()),
            language=self.language_var.get(),
            gender=self.gender_var.get(),
            age_range=self.age_var.get(),
            style=self.style_var.get(),
            speed=self.speed_var.get(),
            pitch=self.pitch_var.get(),
            volume=self.volume_var.get()
        )
        
        # Generate test audio
        asset_id = self.voice_manager.generate_voice_asset(
            test_text, temp_profile.id, emotion="neutral"
        )
        
        if asset_id:
            messagebox.showinfo("Test Complete", "Voice test generated successfully!")
            # Optionally play the test audio here
        else:
            messagebox.showerror("Test Failed", "Failed to generate test voice.")
    
    def _extract_voice_id(self, voice_selection):
        """Extract voice ID from dropdown selection."""
        if "(" in voice_selection and ")" in voice_selection:
            return voice_selection.split("(")[-1].rstrip(")")
        return voice_selection
    
    def _save_profile(self):
        """Save the voice profile."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Invalid Input", "Please enter a profile name.")
            return
        
        voice_id = self._extract_voice_id(self.voice_id_var.get())
        if not voice_id or voice_id in ["Select voice...", "Provider not configured"]:
            messagebox.showerror("Invalid Input", "Please select a valid voice.")
            return
        
        # Create or update profile
        import uuid
        profile_id = self.profile.id if self.profile else str(uuid.uuid4())
        
        profile = VoiceProfile(
            id=profile_id,
            name=name,
            provider=self.provider_var.get(),
            voice_id=voice_id,
            language=self.language_var.get(),
            gender=self.gender_var.get(),
            age_range=self.age_var.get(),
            style=self.style_var.get(),
            speed=self.speed_var.get(),
            pitch=self.pitch_var.get(),
            volume=self.volume_var.get(),
            description=self.description_text.get("1.0", tk.END).strip(),
            usage_count=self.profile.usage_count if self.profile else 0
        )
        
        if self.mode == "create":
            success = self.voice_manager.add_voice_profile(profile)
        else:
            success = self.voice_manager.update_voice_profile(profile)
        
        if success:
            self.destroy()
        else:
            messagebox.showerror("Save Failed", "Failed to save voice profile.")


class TTSConfigDialog(ctk.CTkToplevel):
    """Dialog for configuring TTS providers."""
    
    def __init__(self, parent, tts_manager):
        super().__init__(parent)
        self.tts_manager = tts_manager
        
        self.title("Configure TTS Providers")
        self.geometry("600x400")
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the configuration UI."""
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            main_frame,
            text="TTS Provider Configuration",
            font=FONT_TITLE
        ).pack(pady=(10, 20))
        
        # Provider tabs
        tab_view = ctk.CTkTabview(main_frame)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # OpenAI Tab
        openai_tab = tab_view.add("OpenAI")
        self._create_openai_config(openai_tab)
        
        # Azure Tab
        azure_tab = tab_view.add("Azure")
        self._create_azure_config(azure_tab)
        
        # Google Tab
        google_tab = tab_view.add("Google")
        self._create_google_config(google_tab)
        
        # Close button
        ctk.CTkButton(
            main_frame,
            text="Close",
            command=self.destroy
        ).pack(pady=10)
    
    def _create_openai_config(self, parent):
        """Create OpenAI configuration UI."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="OpenAI API Key:", font=FONT_SUBTITLE_SMALL).pack(anchor="w", pady=(0, 5))
        
        api_key_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Enter OpenAI API key")
        api_key_entry.pack(fill="x", pady=(0, 10))
        
        def configure_openai():
            api_key = api_key_entry.get().strip()
            if api_key:
                success = self.tts_manager.configure_provider("openai", {"api_key": api_key})
                if success:
                    messagebox.showinfo("Success", "OpenAI TTS configured successfully!")
                else:
                    messagebox.showerror("Error", "Failed to configure OpenAI TTS. Check your API key.")
            else:
                messagebox.showwarning("Invalid Input", "Please enter an API key.")
        
        ctk.CTkButton(frame, text="Configure OpenAI", command=configure_openai).pack(pady=5)
        
        # Status
        provider = self.tts_manager.get_provider("openai")
        status = "✅ Configured" if provider and provider.is_configured else "❌ Not configured"
        ctk.CTkLabel(frame, text=f"Status: {status}").pack(pady=10)
    
    def _create_azure_config(self, parent):
        """Create Azure configuration UI."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Azure Speech Key:", font=FONT_SUBTITLE_SMALL).pack(anchor="w", pady=(0, 5))
        key_entry = ctk.CTkEntry(frame, show="*", placeholder_text="Enter Azure Speech key")
        key_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="Azure Region:", font=FONT_SUBTITLE_SMALL).pack(anchor="w", pady=(0, 5))
        region_entry = ctk.CTkEntry(frame, placeholder_text="e.g., eastus, westus2")
        region_entry.pack(fill="x", pady=(0, 10))
        
        def configure_azure():
            key = key_entry.get().strip()
            region = region_entry.get().strip() or "eastus"
            
            if key:
                success = self.tts_manager.configure_provider("azure", {
                    "subscription_key": key,
                    "region": region
                })
                if success:
                    messagebox.showinfo("Success", "Azure TTS configured successfully!")
                else:
                    messagebox.showerror("Error", "Failed to configure Azure TTS. Check your credentials.")
            else:
                messagebox.showwarning("Invalid Input", "Please enter a subscription key.")
        
        ctk.CTkButton(frame, text="Configure Azure", command=configure_azure).pack(pady=5)
        
        # Status
        provider = self.tts_manager.get_provider("azure")
        status = "✅ Configured" if provider and provider.is_configured else "❌ Not configured"
        ctk.CTkLabel(frame, text=f"Status: {status}").pack(pady=10)
    
    def _create_google_config(self, parent):
        """Create Google configuration UI."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Service Account JSON File:", font=FONT_SUBTITLE_SMALL).pack(anchor="w", pady=(0, 5))
        
        file_frame = ctk.CTkFrame(frame, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 10))
        file_frame.grid_columnconfigure(0, weight=1)
        
        file_entry = ctk.CTkEntry(file_frame, placeholder_text="Path to service account JSON file")
        file_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Service Account JSON File",
                filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                file_entry.delete(0, tk.END)
                file_entry.insert(0, file_path)
        
        ctk.CTkButton(file_frame, text="Browse", command=browse_file, width=80).grid(row=0, column=1)
        
        def configure_google():
            file_path = file_entry.get().strip()
            if file_path:
                success = self.tts_manager.configure_provider("google", {
                    "credentials_path": file_path
                })
                if success:
                    messagebox.showinfo("Success", "Google TTS configured successfully!")
                else:
                    messagebox.showerror("Error", "Failed to configure Google TTS. Check your credentials file.")
            else:
                messagebox.showwarning("Invalid Input", "Please select a credentials file.")
        
        ctk.CTkButton(frame, text="Configure Google", command=configure_google).pack(pady=5)
        
        # Status
        provider = self.tts_manager.get_provider("google")
        status = "✅ Configured" if provider and provider.is_configured else "❌ Not configured"
        ctk.CTkLabel(frame, text=f"Status: {status}").pack(pady=10)


class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog for long-running operations."""
    
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.transient(parent)
        self.grab_set()
        
        # Prevent closing
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(main_frame, text="Initializing...", font=FONT_SUBTITLE_SMALL)
        self.status_label.pack(pady=(10, 20))
        
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar.set(0)
    
    def update_progress(self, percent, status_text):
        """Update progress bar and status."""
        self.progress_bar.set(percent / 100.0)
        self.status_label.configure(text=status_text)
        self.update()  # Force UI update