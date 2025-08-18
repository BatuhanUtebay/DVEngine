# dvge/ui/windows/asset_library_window.py

"""Advanced Asset Library Browser for DVGE Media System."""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
from typing import TYPE_CHECKING, Optional, Callable, List
from PIL import Image, ImageTk

if TYPE_CHECKING:
    from ...features.media_system import MediaLibrary, MediaAsset

try:
    from ...features.media_system import MediaType, MediaLibrary, MediaAsset
    MEDIA_SYSTEM_AVAILABLE = True
except ImportError:
    MEDIA_SYSTEM_AVAILABLE = False


class AssetLibraryWindow(ctk.CTkToplevel):
    """Advanced asset library browser and management window."""

    def __init__(self, parent, media_library: Optional['MediaLibrary'] = None, 
                 current_node=None, on_asset_selected: Optional[Callable[[str], None]] = None):
        super().__init__(parent)
        
        self.media_library = media_library
        self.current_node = current_node
        self.on_asset_selected = on_asset_selected
        
        # Window settings
        self.title("Asset Library Browser")
        self.geometry("1000x700")
        self.transient(parent)
        
        # State
        self.current_filter = "all"
        self.selected_asset = None
        self.thumbnail_cache = {}
        
        # UI components
        self.asset_list_frame = None
        self.preview_frame = None
        self.details_frame = None
        
        self.setup_ui()
        self.load_assets()

    def setup_ui(self):
        """Setup the asset library UI."""
        if not MEDIA_SYSTEM_AVAILABLE:
            error_label = ctk.CTkLabel(
                self,
                text="Media System Error\n\nThe advanced media system is not available.",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.pack(expand=True)
            return

        # Main layout
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        self.setup_header(main_frame)
        
        # Content area
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Left panel - Asset list
        self.setup_asset_list(content_frame)
        
        # Right panel - Preview and details
        self.setup_preview_panel(content_frame)

    def setup_header(self, parent):
        """Setup the header with filters and controls."""
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", pady=(0, 10))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Asset Library",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=10)

        # Filter controls
        filter_frame = ctk.CTkFrame(header_frame)
        filter_frame.pack(side="left", padx=20, pady=5)

        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=5)
        
        self.filter_var = ctk.StringVar(value="all")
        filter_combo = ctk.CTkComboBox(
            filter_frame,
            variable=self.filter_var,
            values=["all", "image", "video", "audio", "music"],
            command=self._on_filter_change
        )
        filter_combo.pack(side="left", padx=5)

        # Search
        search_frame = ctk.CTkFrame(header_frame)
        search_frame.pack(side="left", padx=10, pady=5)

        ctk.CTkLabel(search_frame, text="Search:").pack(side="left", padx=5)
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search assets..."
        )
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", self._on_search_change)

        # Action buttons
        button_frame = ctk.CTkFrame(header_frame)
        button_frame.pack(side="right", padx=10, pady=5)

        ctk.CTkButton(
            button_frame,
            text="Import Assets",
            command=self._import_assets,
            width=120
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.load_assets,
            width=80
        ).pack(side="right", padx=5)

    def setup_asset_list(self, parent):
        """Setup the asset list panel."""
        # Left panel container
        left_panel = ctk.CTkFrame(parent)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Asset list header
        list_header = ctk.CTkFrame(left_panel)
        list_header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            list_header,
            text="Assets",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=10)

        # Asset count
        self.asset_count_label = ctk.CTkLabel(
            list_header,
            text="0 assets",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.asset_count_label.pack(side="right", padx=10)

        # Asset list container
        self.asset_list_frame = ctk.CTkScrollableFrame(left_panel)
        self.asset_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Asset controls
        controls_frame = ctk.CTkFrame(left_panel)
        controls_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            controls_frame,
            text="Add to Node",
            command=self._add_selected_to_node,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            controls_frame,
            text="Delete Asset",
            command=self._delete_selected_asset,
            width=100,
            fg_color="red",
            hover_color="darkred"
        ).pack(side="right", padx=5)

    def setup_preview_panel(self, parent):
        """Setup the preview and details panel."""
        # Right panel container
        right_panel = ctk.CTkFrame(parent)
        right_panel.pack(side="right", fill="y", padx=(5, 0))
        right_panel.configure(width=350)

        # Preview section
        preview_header = ctk.CTkFrame(right_panel)
        preview_header.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(
            preview_header,
            text="Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=10, pady=5)

        # Preview area
        self.preview_frame = ctk.CTkFrame(right_panel)
        self.preview_frame.pack(fill="x", padx=5, pady=5, ipady=20)
        self.preview_frame.configure(height=200)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Select an asset to preview",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        self.preview_label.pack(expand=True)

        # Details section
        details_header = ctk.CTkFrame(right_panel)
        details_header.pack(fill="x", padx=5, pady=(10, 5))

        ctk.CTkLabel(
            details_header,
            text="Details",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=10, pady=5)

        # Details area
        self.details_frame = ctk.CTkScrollableFrame(right_panel)
        self.details_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Properties section
        props_header = ctk.CTkFrame(right_panel)
        props_header.pack(fill="x", padx=5, pady=(10, 5))

        ctk.CTkLabel(
            props_header,
            text="Transform Properties",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=10, pady=5)

        # Quick property controls
        self.setup_property_controls(right_panel)

    def setup_property_controls(self, parent):
        """Setup quick property editing controls."""
        props_frame = ctk.CTkFrame(parent)
        props_frame.pack(fill="x", padx=5, pady=5)

        # Position
        pos_frame = ctk.CTkFrame(props_frame)
        pos_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(pos_frame, text="Position:", width=80).pack(side="left", padx=5)
        self.x_var = ctk.DoubleVar()
        self.x_entry = ctk.CTkEntry(pos_frame, textvariable=self.x_var, width=60)
        self.x_entry.pack(side="left", padx=2)
        self.x_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(pos_frame, text="x", width=15).pack(side="left")

        self.y_var = ctk.DoubleVar()
        self.y_entry = ctk.CTkEntry(pos_frame, textvariable=self.y_var, width=60)
        self.y_entry.pack(side="left", padx=2)
        self.y_entry.bind("<KeyRelease>", self._on_property_change)

        # Size
        size_frame = ctk.CTkFrame(props_frame)
        size_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(size_frame, text="Size:", width=80).pack(side="left", padx=5)
        self.width_var = ctk.DoubleVar(value=100)
        self.width_entry = ctk.CTkEntry(size_frame, textvariable=self.width_var, width=60)
        self.width_entry.pack(side="left", padx=2)
        self.width_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(size_frame, text="w", width=15).pack(side="left")

        self.height_var = ctk.DoubleVar(value=100)
        self.height_entry = ctk.CTkEntry(size_frame, textvariable=self.height_var, width=60)
        self.height_entry.pack(side="left", padx=2)
        self.height_entry.bind("<KeyRelease>", self._on_property_change)

        # Rotation and Opacity
        rot_frame = ctk.CTkFrame(props_frame)
        rot_frame.pack(fill="x", padx=5, pady=2)

        ctk.CTkLabel(rot_frame, text="Rotation:", width=80).pack(side="left", padx=5)
        self.rotation_var = ctk.DoubleVar()
        self.rotation_entry = ctk.CTkEntry(rot_frame, textvariable=self.rotation_var, width=60)
        self.rotation_entry.pack(side="left", padx=2)
        self.rotation_entry.bind("<KeyRelease>", self._on_property_change)

        ctk.CTkLabel(rot_frame, text="Opacity:", width=60).pack(side="left", padx=(10, 5))
        self.opacity_var = ctk.DoubleVar(value=1.0)
        self.opacity_entry = ctk.CTkEntry(rot_frame, textvariable=self.opacity_var, width=60)
        self.opacity_entry.pack(side="left", padx=2)
        self.opacity_entry.bind("<KeyRelease>", self._on_property_change)

    def load_assets(self):
        """Load and display assets in the library."""
        # Clear existing assets
        for widget in self.asset_list_frame.winfo_children():
            widget.destroy()

        if not self.media_library:
            no_library_label = ctk.CTkLabel(
                self.asset_list_frame,
                text="No media library available",
                text_color="#666666"
            )
            no_library_label.pack(pady=20)
            return

        # Get filtered assets
        assets = self._get_filtered_assets()

        # Update count
        self.asset_count_label.configure(text=f"{len(assets)} assets")

        if not assets:
            no_assets_label = ctk.CTkLabel(
                self.asset_list_frame,
                text="No assets found",
                text_color="#666666"
            )
            no_assets_label.pack(pady=20)
            return

        # Create asset items
        for asset in assets:
            self._create_asset_item(asset)

    def _get_filtered_assets(self) -> List['MediaAsset']:
        """Get assets filtered by current filter and search."""
        if not self.media_library:
            return []

        assets = list(self.media_library.assets.values())

        # Apply type filter
        if self.current_filter != "all":
            assets = [a for a in assets if a.media_type.value == self.current_filter]

        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            assets = [a for a in assets if search_term in a.name.lower()]

        # Sort by name
        assets.sort(key=lambda a: a.name)

        return assets

    def _create_asset_item(self, asset: 'MediaAsset'):
        """Create an asset item widget."""
        # Asset container
        asset_frame = ctk.CTkFrame(self.asset_list_frame)
        asset_frame.pack(fill="x", padx=5, pady=2)

        # Asset info
        info_frame = ctk.CTkFrame(asset_frame)
        info_frame.pack(fill="x", padx=5, pady=5)

        # Asset type icon and name
        name_frame = ctk.CTkFrame(info_frame)
        name_frame.pack(fill="x")

        # Type badge
        type_color = {
            "image": "#4CAF50",
            "video": "#FF5722", 
            "audio": "#2196F3",
            "music": "#9C27B0"
        }.get(asset.media_type.value, "#757575")

        type_label = ctk.CTkLabel(
            name_frame,
            text=asset.media_type.value.upper(),
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=type_color,
            corner_radius=10,
            width=60
        )
        type_label.pack(side="left", padx=5, pady=2)

        # Asset name (clickable)
        name_label = ctk.CTkLabel(
            name_frame,
            text=asset.name,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=10)

        # File size and properties
        file_size = self._get_file_size(asset.file_path)
        props_text = f"Size: {file_size}"
        
        if asset.animations:
            props_text += f" • {len(asset.animations)} animations"
        if asset.effects:
            props_text += f" • {len(asset.effects)} effects"

        props_label = ctk.CTkLabel(
            info_frame,
            text=props_text,
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        props_label.pack(anchor="w", padx=5)

        # Make clickable
        def select_asset(event=None):
            self._select_asset(asset)

        for widget in [asset_frame, info_frame, name_frame, name_label]:
            widget.bind("<Button-1>", select_asset)
            widget.configure(cursor="hand2")

    def _get_file_size(self, file_path: str) -> str:
        """Get human-readable file size."""
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if size < 1024:
                    return f"{size} B"
                elif size < 1024 * 1024:
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
        except:
            pass
        return "Unknown"

    def _select_asset(self, asset: 'MediaAsset'):
        """Select an asset and update preview/details."""
        self.selected_asset = asset
        self._update_preview(asset)
        self._update_details(asset)
        self._load_asset_properties(asset)

    def _update_preview(self, asset: 'MediaAsset'):
        """Update the preview area."""
        # Clear previous preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        try:
            if asset.media_type.value == "image":
                self._show_image_preview(asset)
            elif asset.media_type.value == "video":
                self._show_video_preview(asset)
            else:
                self._show_generic_preview(asset)
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.preview_frame,
                text=f"Preview error:\n{str(e)}",
                text_color="red"
            )
            error_label.pack(expand=True)

    def _show_image_preview(self, asset: 'MediaAsset'):
        """Show image preview."""
        if not os.path.exists(asset.file_path):
            ctk.CTkLabel(
                self.preview_frame,
                text="File not found",
                text_color="red"
            ).pack(expand=True)
            return

        try:
            # Load and resize image
            image = Image.open(asset.file_path)
            image.thumbnail((300, 180), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Display image
            image_label = tk.Label(
                self.preview_frame,
                image=photo,
                bg="#2b2b2b"
            )
            image_label.image = photo  # Keep a reference
            image_label.pack(expand=True)
            
        except Exception as e:
            ctk.CTkLabel(
                self.preview_frame,
                text=f"Cannot preview image:\n{str(e)}",
                text_color="orange"
            ).pack(expand=True)

    def _show_video_preview(self, asset: 'MediaAsset'):
        """Show video preview (placeholder)."""
        preview_frame = ctk.CTkFrame(self.preview_frame)
        preview_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            preview_frame,
            text="🎥",
            font=ctk.CTkFont(size=48)
        ).pack(pady=10)

        ctk.CTkLabel(
            preview_frame,
            text="Video Preview",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack()

        ctk.CTkLabel(
            preview_frame,
            text=f"Duration: {asset.duration_override or 'Auto'}",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        ).pack(pady=5)

    def _show_generic_preview(self, asset: 'MediaAsset'):
        """Show generic preview for other media types."""
        preview_frame = ctk.CTkFrame(self.preview_frame)
        preview_frame.pack(expand=True, fill="both", padx=20, pady=20)

        icons = {
            "audio": "🔊",
            "music": "🎵"
        }

        ctk.CTkLabel(
            preview_frame,
            text=icons.get(asset.media_type.value, "📄"),
            font=ctk.CTkFont(size=48)
        ).pack(pady=10)

        ctk.CTkLabel(
            preview_frame,
            text=asset.media_type.value.title(),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack()

    def _update_details(self, asset: 'MediaAsset'):
        """Update the details panel."""
        # Clear previous details
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # Asset details
        details = [
            ("Name:", asset.name),
            ("Type:", asset.media_type.value.title()),
            ("File:", os.path.basename(asset.file_path)),
            ("Size:", self._get_file_size(asset.file_path)),
            ("Animations:", len(asset.animations)),
            ("Effects:", len(asset.effects)),
            ("Position:", f"{asset.x}%, {asset.y}%"),
            ("Size:", f"{asset.width}% × {asset.height}%"),
            ("Rotation:", f"{asset.rotation}°"),
            ("Opacity:", f"{asset.opacity:.2f}"),
            ("Z-Index:", asset.z_index)
        ]

        if asset.media_type.value in ["video", "audio"]:
            details.extend([
                ("Autoplay:", "Yes" if asset.autoplay else "No"),
                ("Loop:", "Yes" if asset.loop else "No"),
                ("Volume:", f"{asset.volume:.2f}"),
                ("Start Time:", f"{asset.start_time}s")
            ])

        for label, value in details:
            detail_frame = ctk.CTkFrame(self.details_frame)
            detail_frame.pack(fill="x", padx=5, pady=1)

            ctk.CTkLabel(
                detail_frame,
                text=label,
                font=ctk.CTkFont(weight="bold"),
                width=80
            ).pack(side="left", padx=5)

            ctk.CTkLabel(
                detail_frame,
                text=str(value),
                anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=5)

    def _load_asset_properties(self, asset: 'MediaAsset'):
        """Load asset properties into the property controls."""
        self.x_var.set(asset.x)
        self.y_var.set(asset.y)
        self.width_var.set(asset.width)
        self.height_var.set(asset.height)
        self.rotation_var.set(asset.rotation)
        self.opacity_var.set(asset.opacity)

    def _on_property_change(self, event=None):
        """Handle property changes."""
        if not self.selected_asset:
            return

        try:
            # Update asset properties
            self.selected_asset.x = self.x_var.get()
            self.selected_asset.y = self.y_var.get()
            self.selected_asset.width = self.width_var.get()
            self.selected_asset.height = self.height_var.get()
            self.selected_asset.rotation = self.rotation_var.get()
            self.selected_asset.opacity = self.opacity_var.get()

            # Update details display
            self._update_details(self.selected_asset)

        except (ValueError, tk.TclError):
            pass  # Handle invalid input gracefully

    def _on_filter_change(self, value):
        """Handle filter change."""
        self.current_filter = value
        self.load_assets()

    def _on_search_change(self, event=None):
        """Handle search change."""
        self.load_assets()

    def _import_assets(self):
        """Import new assets."""
        filetypes = [
            ("All Supported", "*.png *.jpg *.jpeg *.gif *.webp *.mp4 *.webm *.ogg *.avi *.mov *.mp3 *.wav *.m4a"),
            ("Images", "*.png *.jpg *.jpeg *.gif *.webp"),
            ("Videos", "*.mp4 *.webm *.ogg *.avi *.mov"),
            ("Audio", "*.mp3 *.wav *.ogg *.m4a"),
            ("All files", "*.*")
        ]

        filepaths = filedialog.askopenfilenames(
            title="Import Media Assets",
            filetypes=filetypes
        )

        if not filepaths or not self.media_library:
            return

        imported_count = 0
        for filepath in filepaths:
            asset = self.media_library.add_asset(filepath)
            if asset:
                imported_count += 1

        messagebox.showinfo(
            "Import Complete",
            f"Successfully imported {imported_count} of {len(filepaths)} assets."
        )

        self.load_assets()

    def _add_selected_to_node(self):
        """Add selected asset to current node."""
        if not self.selected_asset or not self.current_node:
            messagebox.showerror("Error", "No asset selected or no node available")
            return

        if self.on_asset_selected:
            self.on_asset_selected(self.selected_asset.asset_id)
            messagebox.showinfo("Success", f"Added '{self.selected_asset.name}' to node")

    def _delete_selected_asset(self):
        """Delete selected asset from library."""
        if not self.selected_asset:
            messagebox.showerror("Error", "No asset selected")
            return

        if messagebox.askyesno(
            "Confirm Delete", 
            f"Delete '{self.selected_asset.name}' from the library?\n\nThis cannot be undone."
        ):
            if self.media_library:
                self.media_library.remove_asset(self.selected_asset.asset_id)
                messagebox.showinfo("Success", "Asset deleted from library")
                self.selected_asset = None
                self.load_assets()
                
                # Clear preview and details
                for widget in self.preview_frame.winfo_children():
                    widget.destroy()
                for widget in self.details_frame.winfo_children():
                    widget.destroy()
                    
                self.preview_label = ctk.CTkLabel(
                    self.preview_frame,
                    text="Select an asset to preview",
                    font=ctk.CTkFont(size=12),
                    text_color="#666666"
                )
                self.preview_label.pack(expand=True)