# dvge/ui/panels/marketplace_panel.py

"""Community Marketplace UI Panel."""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, List, Optional, Any
from ...constants import *
from ...features.marketplace_system import MarketplaceManager, ContentMetadata, ContentType, ContentCategory


class MarketplacePanel(ctk.CTkFrame):
    """UI panel for community marketplace functionality."""
    
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_SECONDARY_FRAME)
        self.app = app
        
        # Initialize marketplace manager if not already done
        if not hasattr(app, 'marketplace_manager'):
            from ...features.marketplace_system import MarketplaceManager
            app.marketplace_manager = MarketplaceManager(app)
        
        self.marketplace_manager = app.marketplace_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_tab_view()
        
        # Populate sample content for demonstration
        if not self.marketplace_manager.content_catalog:
            self.marketplace_manager.populate_sample_content()
    
    def _create_header(self):
        """Create the panel header."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header, 
            text="🏪 Community Marketplace", 
            font=FONT_SUBTITLE
        ).grid(row=0, column=0, sticky="w")
        
        # User status
        self.user_status_label = ctk.CTkLabel(
            header, 
            text="Not logged in", 
            font=FONT_SMALL
        )
        self.user_status_label.grid(row=0, column=1, sticky="e")
        
        self._update_user_status()
    
    def _create_tab_view(self):
        """Create the main tab view."""
        self.tab_view = ctk.CTkTabview(
            self,
            fg_color=COLOR_PRIMARY_FRAME,
            segmented_button_fg_color=COLOR_SECONDARY_FRAME,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER
        )
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Create tabs
        self.tab_view.add("Browse")
        self.tab_view.add("My Content")
        self.tab_view.add("Upload")
        self.tab_view.add("Account")
        
        # Initialize tab content
        self._create_browse_tab()
        self._create_my_content_tab()
        self._create_upload_tab()
        self._create_account_tab()
    
    def _create_browse_tab(self):
        """Create browse content tab."""
        browse_frame = self.tab_view.tab("Browse")
        browse_frame.grid_columnconfigure(0, weight=1)
        browse_frame.grid_rowconfigure(2, weight=1)
        
        # Search section
        search_frame = ctk.CTkFrame(browse_frame, fg_color=COLOR_BACKGROUND)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(search_frame, text="Search:", font=FONT_SMALL).grid(
            row=0, column=0, padx=(10, 5), pady=10
        )
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search content...")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            width=80,
            command=self._search_content
        ).grid(row=0, column=2, padx=(5, 10), pady=10)
        
        # Filters section
        filters_frame = ctk.CTkFrame(browse_frame, fg_color=COLOR_BACKGROUND)
        filters_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        filters_frame.grid_columnconfigure(0, weight=1)
        filters_frame.grid_columnconfigure(1, weight=1)
        filters_frame.grid_columnconfigure(2, weight=1)
        
        # Content type filter
        ctk.CTkLabel(filters_frame, text="Type:", font=FONT_SMALL).grid(
            row=0, column=0, sticky="w", padx=(10, 5), pady=5
        )
        
        self.type_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["All Types"] + [t.value.replace("_", " ").title() for t in ContentType],
            command=self._on_filter_changed
        )
        self.type_filter.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=(0, 10))
        
        # Category filter
        ctk.CTkLabel(filters_frame, text="Category:", font=FONT_SMALL).grid(
            row=0, column=1, sticky="w", padx=5, pady=5
        )
        
        self.category_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["All Categories"] + [c.value.replace("_", " ").title() for c in ContentCategory],
            command=self._on_filter_changed
        )
        self.category_filter.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))
        
        # Sort by
        ctk.CTkLabel(filters_frame, text="Sort by:", font=FONT_SMALL).grid(
            row=0, column=2, sticky="w", padx=(5, 10), pady=5
        )
        
        self.sort_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=["Popularity", "Rating", "Newest", "Title"],
            command=self._on_filter_changed
        )
        self.sort_filter.grid(row=1, column=2, sticky="ew", padx=(5, 10), pady=(0, 10))
        
        # Content list
        self.content_list = ctk.CTkScrollableFrame(browse_frame, fg_color=COLOR_BACKGROUND)
        self.content_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.content_list.grid_columnconfigure(0, weight=1)
        
        self._refresh_content_list()
    
    def _create_my_content_tab(self):
        """Create my content tab."""
        my_content_frame = self.tab_view.tab("My Content")
        my_content_frame.grid_columnconfigure(0, weight=1)
        my_content_frame.grid_rowconfigure(1, weight=1)
        
        # Header with stats
        stats_frame = ctk.CTkFrame(my_content_frame, fg_color=COLOR_BACKGROUND)
        stats_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.my_stats_label = ctk.CTkLabel(
            stats_frame,
            text="Login to view your content",
            font=FONT_SMALL
        )
        self.my_stats_label.pack(padx=10, pady=10)
        
        # My uploads list
        self.my_uploads_list = ctk.CTkScrollableFrame(my_content_frame, fg_color=COLOR_BACKGROUND)
        self.my_uploads_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.my_uploads_list.grid_columnconfigure(0, weight=1)
        
        self._refresh_my_content()
    
    def _create_upload_tab(self):
        """Create upload content tab."""
        upload_frame = self.tab_view.tab("Upload")
        upload_frame.grid_columnconfigure(0, weight=1)
        
        # Upload form
        form_frame = ctk.CTkScrollableFrame(upload_frame, fg_color=COLOR_BACKGROUND)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        ctk.CTkLabel(form_frame, text="Title:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.upload_title_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter content title...")
        self.upload_title_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Description
        ctk.CTkLabel(form_frame, text="Description:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="nw", padx=10, pady=5
        )
        self.upload_description = ctk.CTkTextbox(form_frame, height=80)
        self.upload_description.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Content type
        ctk.CTkLabel(form_frame, text="Type:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.upload_type = ctk.CTkOptionMenu(
            form_frame,
            values=[t.value.replace("_", " ").title() for t in ContentType]
        )
        self.upload_type.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Category
        ctk.CTkLabel(form_frame, text="Category:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.upload_category = ctk.CTkOptionMenu(
            form_frame,
            values=[c.value.replace("_", " ").title() for c in ContentCategory]
        )
        self.upload_category.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Tags
        ctk.CTkLabel(form_frame, text="Tags:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.upload_tags_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Enter tags separated by commas..."
        )
        self.upload_tags_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Upload Current Project",
            command=self._upload_current_project
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Upload from File",
            command=self._upload_from_file
        ).pack(side="left")
    
    def _create_account_tab(self):
        """Create account management tab."""
        account_frame = self.tab_view.tab("Account")
        account_frame.grid_columnconfigure(0, weight=1)
        
        # Login section
        self.login_frame = ctk.CTkFrame(account_frame, fg_color=COLOR_BACKGROUND)
        self.login_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.login_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.login_frame, text="Username:", font=FONT_SMALL).grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter username")
        self.username_entry.grid(row=0, column=1, sticky="ew", padx=(10, 10), pady=5)
        
        ctk.CTkLabel(self.login_frame, text="Password:", font=FONT_SMALL).grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter password", show="*")
        self.password_entry.grid(row=1, column=1, sticky="ew", padx=(10, 10), pady=5)
        
        login_buttons = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        login_buttons.grid(row=2, column=0, columnspan=2, pady=10)
        
        ctk.CTkButton(
            login_buttons,
            text="Login",
            command=self._login_user
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            login_buttons,
            text="Demo Login",
            command=self._demo_login
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            login_buttons,
            text="Register",
            command=self._show_register_dialog
        ).pack(side="left")
        
        # User info section (hidden by default)
        self.user_info_frame = ctk.CTkFrame(account_frame, fg_color=COLOR_BACKGROUND)
        self.user_info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.user_info_label = ctk.CTkLabel(
            self.user_info_frame,
            text="",
            font=FONT_SMALL,
            justify="left"
        )
        self.user_info_label.pack(padx=10, pady=10)
        
        self.logout_button = ctk.CTkButton(
            self.user_info_frame,
            text="Logout",
            command=self._logout_user
        )
        self.logout_button.pack(pady=10)
        
        self._update_account_display()
    
    def _update_user_status(self):
        """Update user status in header."""
        if self.marketplace_manager.is_logged_in():
            user = self.marketplace_manager.current_user
            self.user_status_label.configure(
                text=f"Logged in as: {user.display_name}"
            )
        else:
            self.user_status_label.configure(text="Not logged in")
    
    def _update_account_display(self):
        """Update account tab display based on login status."""
        if self.marketplace_manager.is_logged_in():
            self.login_frame.grid_remove()
            self.user_info_frame.grid()
            
            user = self.marketplace_manager.current_user
            info_text = f"""Display Name: {user.display_name}
Username: {user.username}
Email: {user.email}
Reputation: {user.reputation_score}
Uploads: {user.upload_count}
Downloads: {user.download_count}
Verified: {'Yes' if user.verified else 'No'}"""
            
            self.user_info_label.configure(text=info_text)
        else:
            self.login_frame.grid()
            self.user_info_frame.grid_remove()
    
    def _search_content(self):
        """Search for content."""
        query = self.search_entry.get().strip()
        self._refresh_content_list(query)
    
    def _on_filter_changed(self, value=None):
        """Handle filter changes."""
        self._refresh_content_list()
    
    def _refresh_content_list(self, query: str = ""):
        """Refresh the content list display."""
        # Clear existing content
        for widget in self.content_list.winfo_children():
            widget.destroy()
        
        # Get filter values
        content_type = None
        type_value = self.type_filter.get()
        if type_value != "All Types":
            content_type = type_value.lower().replace(" ", "_")
        
        category = None
        category_value = self.category_filter.get()
        if category_value != "All Categories":
            category = category_value.lower().replace(" ", "_")
        
        sort_by = self.sort_filter.get().lower()
        
        # Search content
        results = self.marketplace_manager.search_content(
            query=query,
            content_type=content_type,
            category=category,
            sort_by=sort_by,
            limit=50
        )
        
        if not results:
            no_results = ctk.CTkLabel(
                self.content_list,
                text="No content found",
                font=FONT_SMALL
            )
            no_results.grid(row=0, column=0, pady=20)
            return
        
        # Display results
        for i, content in enumerate(results):
            self._create_content_item(self.content_list, content, i)
    
    def _create_content_item(self, parent, content: ContentMetadata, row: int):
        """Create a content item widget."""
        item_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
        item_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Content info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Title and author
        title_text = f"{content.title} v{content.version}"
        ctk.CTkLabel(
            info_frame,
            text=title_text,
            font=FONT_SUBTITLE_SMALL,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        author_text = f"by {content.author_name}"
        ctk.CTkLabel(
            info_frame,
            text=author_text,
            font=FONT_SMALL,
            anchor="e"
        ).grid(row=0, column=1, sticky="e")
        
        # Description
        desc_text = content.description[:100]
        if len(content.description) > 100:
            desc_text += "..."
        
        ctk.CTkLabel(
            info_frame,
            text=desc_text,
            font=FONT_SMALL,
            wraplength=300,
            anchor="w",
            justify="left"
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        
        # Stats and controls
        stats_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 5))
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Stats
        stats_text = f"⭐ {content.rating_average:.1f} ({content.rating_count}) | 📥 {content.download_count} | {content.content_type.replace('_', ' ').title()}"
        ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=FONT_SMALL
        ).grid(row=0, column=0, sticky="w")
        
        # Download button
        ctk.CTkButton(
            stats_frame,
            text="Download",
            width=80,
            height=24,
            command=lambda c=content: self._download_content(c)
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))
    
    def _download_content(self, content: ContentMetadata):
        """Download and install content."""
        try:
            file_path = self.marketplace_manager.download_content(content.id)
            if file_path:
                # Ask user if they want to install
                if messagebox.askyesno(
                    "Content Downloaded",
                    f"'{content.title}' has been downloaded.\n\nWould you like to install it now?"
                ):
                    if self.marketplace_manager.install_content(content.id):
                        messagebox.showinfo(
                            "Installation Complete",
                            f"'{content.title}' has been installed successfully!"
                        )
                        # Refresh UI if needed
                        if hasattr(self.app, 'canvas_manager'):
                            self.app.canvas_manager.redraw_all_nodes()
                        if hasattr(self.app, 'properties_panel'):
                            self.app.properties_panel.update_all_panels()
                    else:
                        messagebox.showerror("Installation Failed", "Failed to install content.")
                else:
                    messagebox.showinfo(
                        "Download Complete",
                        f"'{content.title}' has been downloaded to your cache."
                    )
            else:
                messagebox.showerror("Download Failed", "Failed to download content.")
        except Exception as e:
            messagebox.showerror("Error", f"Error downloading content: {str(e)}")
    
    def _refresh_my_content(self):
        """Refresh my content tab."""
        # Clear existing content
        for widget in self.my_uploads_list.winfo_children():
            widget.destroy()
        
        if not self.marketplace_manager.is_logged_in():
            login_prompt = ctk.CTkLabel(
                self.my_uploads_list,
                text="Please login to view your uploaded content",
                font=FONT_SMALL
            )
            login_prompt.grid(row=0, column=0, pady=20)
            return
        
        # Update stats
        user = self.marketplace_manager.current_user
        stats_text = f"Uploads: {user.upload_count} | Downloads: {user.download_count} | Reputation: {user.reputation_score}"
        self.my_stats_label.configure(text=stats_text)
        
        # Get user uploads
        uploads = self.marketplace_manager.get_user_uploads()
        
        if not uploads:
            no_uploads = ctk.CTkLabel(
                self.my_uploads_list,
                text="You haven't uploaded any content yet",
                font=FONT_SMALL
            )
            no_uploads.grid(row=0, column=0, pady=20)
            return
        
        # Display uploads
        for i, content in enumerate(uploads):
            self._create_my_content_item(self.my_uploads_list, content, i)
    
    def _create_my_content_item(self, parent, content: ContentMetadata, row: int):
        """Create a my content item widget."""
        item_frame = ctk.CTkFrame(parent, fg_color=COLOR_SECONDARY_FRAME)
        item_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        item_frame.grid_columnconfigure(0, weight=1)
        
        # Content info
        info_text = f"{content.title} v{content.version}\n⭐ {content.rating_average:.1f} ({content.rating_count}) | 📥 {content.download_count}"
        
        ctk.CTkLabel(
            item_frame,
            text=info_text,
            font=FONT_SMALL,
            justify="left"
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    
    def _upload_current_project(self):
        """Upload the current project as marketplace content."""
        if not self.marketplace_manager.is_logged_in():
            messagebox.showwarning("Login Required", "Please login to upload content.")
            return
        
        title = self.upload_title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing Information", "Please enter a title.")
            return
        
        description = self.upload_description.get("1.0", tk.END).strip()
        if not description:
            messagebox.showwarning("Missing Information", "Please enter a description.")
            return
        
        content_type = self.upload_type.get().lower().replace(" ", "_")
        category = self.upload_category.get().lower().replace(" ", "_")
        
        tags_text = self.upload_tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        
        try:
            content_id = self.marketplace_manager.create_content_from_project(
                title, description, content_type, category, tags
            )
            
            if content_id:
                messagebox.showinfo(
                    "Upload Successful",
                    f"'{title}' has been uploaded to the marketplace!"
                )
                
                # Clear form
                self.upload_title_entry.delete(0, tk.END)
                self.upload_description.delete("1.0", tk.END)
                self.upload_tags_entry.delete(0, tk.END)
                
                # Refresh my content
                self._refresh_my_content()
                
                # Update user status
                self._update_user_status()
                
            else:
                messagebox.showerror("Upload Failed", "Failed to upload content.")
                
        except Exception as e:
            messagebox.showerror("Upload Error", f"Error uploading content: {str(e)}")
    
    def _upload_from_file(self):
        """Upload content from a file."""
        messagebox.showinfo("Not Implemented", "Upload from file functionality coming soon!")
    
    def _login_user(self):
        """Login user."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Missing Information", "Please enter username and password.")
            return
        
        if self.marketplace_manager.login_user(username, password):
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            
            # Clear password
            self.password_entry.delete(0, tk.END)
            
            # Update UI
            self._update_user_status()
            self._update_account_display()
            self._refresh_my_content()
            
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    
    def _demo_login(self):
        """Login with demo account."""
        if self.marketplace_manager.login_user("demo_user", "password"):
            messagebox.showinfo("Demo Login", "Logged in as demo user!")
            
            # Update UI
            self._update_user_status()
            self._update_account_display()
            self._refresh_my_content()
        else:
            messagebox.showerror("Demo Login Failed", "Could not login with demo account.")
    
    def _logout_user(self):
        """Logout current user."""
        self.marketplace_manager.logout_user()
        messagebox.showinfo("Logged Out", "You have been logged out.")
        
        # Update UI
        self._update_user_status()
        self._update_account_display()
        self._refresh_my_content()
    
    def _show_register_dialog(self):
        """Show registration dialog."""
        RegisterDialog(self, self.marketplace_manager)
        
        # Update UI after potential registration
        self._update_user_status()
        self._update_account_display()


class RegisterDialog(ctk.CTkToplevel):
    """Registration dialog for new users."""
    
    def __init__(self, parent, marketplace_manager):
        super().__init__(parent)
        self.marketplace_manager = marketplace_manager
        
        self.title("Register New Account")
        self.geometry("400x350")
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
    
    def _create_ui(self):
        """Create registration UI."""
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY_FRAME)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        ctk.CTkLabel(
            main_frame,
            text="Create New Account",
            font=FONT_TITLE
        ).grid(row=row, column=0, columnspan=2, pady=(10, 20))
        row += 1
        
        # Username
        ctk.CTkLabel(main_frame, text="Username:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.username_entry = ctk.CTkEntry(main_frame, placeholder_text="Choose username")
        self.username_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Display name
        ctk.CTkLabel(main_frame, text="Display Name:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.display_name_entry = ctk.CTkEntry(main_frame, placeholder_text="Your display name")
        self.display_name_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Email
        ctk.CTkLabel(main_frame, text="Email:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.email_entry = ctk.CTkEntry(main_frame, placeholder_text="your@email.com")
        self.email_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Password
        ctk.CTkLabel(main_frame, text="Password:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="Choose password", show="*")
        self.password_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Confirm password
        ctk.CTkLabel(main_frame, text="Confirm:", font=FONT_SMALL).grid(
            row=row, column=0, sticky="w", padx=10, pady=5
        )
        self.confirm_password_entry = ctk.CTkEntry(main_frame, placeholder_text="Confirm password", show="*")
        self.confirm_password_entry.grid(row=row, column=1, sticky="ew", padx=(10, 10), pady=5)
        row += 1
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Register",
            command=self._register_user
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side="left")
    
    def _register_user(self):
        """Register the new user."""
        username = self.username_entry.get().strip()
        display_name = self.display_name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([username, email, password]):
            messagebox.showwarning("Missing Information", "Please fill in all required fields.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Weak Password", "Password must be at least 6 characters long.")
            return
        
        # Register user
        try:
            if self.marketplace_manager.register_user(username, email, password, display_name):
                messagebox.showinfo("Registration Successful", f"Welcome to the marketplace, {display_name or username}!")
                self.destroy()
            else:
                messagebox.showerror("Registration Failed", "Failed to register user.")
        except Exception as e:
            messagebox.showerror("Registration Error", f"Error registering user: {str(e)}")