"""AI Settings Dialog for DVGE."""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
import os
from typing import Dict, Any, Optional


class AISettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring AI service settings."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.current_settings = {}
        
        # Window configuration
        self.title("AI Settings")
        self.geometry("700x600")
        self.minsize(600, 500)
        self.configure(fg_color=("#F0F0F0", "#2B2B2B"))
        
        # Make modal
        self.transient(app)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent()
        
        # Load current settings
        self.load_current_settings()
        
        # Setup UI
        self.setup_ui()
        
    def center_on_parent(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        parent_x = self.app.winfo_rootx()
        parent_y = self.app.winfo_rooty()
        parent_width = self.app.winfo_width()
        parent_height = self.app.winfo_height()
        
        x = parent_x + (parent_width - self.winfo_width()) // 2
        y = parent_y + (parent_height - self.winfo_height()) // 2
        
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Set up the dialog UI."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content
        self.create_content()
        
        # Buttons
        self.create_buttons()
    
    def create_header(self):
        """Create the dialog header."""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        ctk.CTkLabel(
            header_frame,
            text="⚙️",
            font=ctk.CTkFont(size=24)
        ).grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Title and description
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=10)
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="AI Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Configure AI providers, API keys, and service settings",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w")
    
    def create_content(self):
        """Create the main content area."""
        # Create notebook for different settings categories
        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Setup tabs
        self.setup_providers_tab()
        self.setup_general_tab()
        self.setup_usage_tab()
        self.setup_advanced_tab()
    
    def setup_providers_tab(self):
        """Set up the AI providers configuration tab."""
        tab = self.notebook.add("Providers")
        
        # Providers frame
        providers_frame = ctk.CTkScrollableFrame(tab)
        providers_frame.pack(fill="both", expand=True, padx=10, pady=10)
        providers_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Default provider selection
        ctk.CTkLabel(
            providers_frame,
            text="Default Provider:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 5))
        
        self.default_provider_var = ctk.StringVar()
        self.default_provider_menu = ctk.CTkOptionMenu(
            providers_frame,
            variable=self.default_provider_var,
            values=["openai", "anthropic", "local", "mock"],
            command=self.on_default_provider_changed
        )
        self.default_provider_menu.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=(10, 5))
        row += 1
        
        # Separator
        ctk.CTkFrame(providers_frame, height=1, fg_color=("gray80", "gray30")).grid(
            row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=10
        )
        row += 1
        
        # OpenAI Configuration
        self.create_openai_config(providers_frame, row)
        row += 6
        
        # Anthropic Configuration
        self.create_anthropic_config(providers_frame, row)
        row += 6
        
        # Local AI Configuration
        self.create_local_ai_config(providers_frame, row)
    
    def create_openai_config(self, parent, start_row):
        """Create OpenAI configuration section."""
        row = start_row
        
        # Header
        ctk.CTkLabel(
            parent,
            text="🤖 OpenAI Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
        row += 1
        
        # API Key
        ctk.CTkLabel(parent, text="API Key:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.openai_key_entry = ctk.CTkEntry(
            parent,
            placeholder_text="sk-...",
            show="*",
            width=300
        )
        self.openai_key_entry.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Model
        ctk.CTkLabel(parent, text="Model:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.openai_model_var = ctk.StringVar(value="gpt-4")
        self.openai_model_menu = ctk.CTkOptionMenu(
            parent,
            variable=self.openai_model_var,
            values=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        )
        self.openai_model_menu.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Max tokens
        ctk.CTkLabel(parent, text="Max Tokens:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.openai_tokens_entry = ctk.CTkEntry(parent, placeholder_text="1000")
        self.openai_tokens_entry.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Test connection button
        self.openai_test_button = ctk.CTkButton(
            parent,
            text="Test Connection",
            command=lambda: self.test_provider_connection("openai"),
            width=120
        )
        self.openai_test_button.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=5)
        row += 1
        
        # Status
        self.openai_status_label = ctk.CTkLabel(
            parent,
            text="Status: Not configured",
            text_color=("gray60", "gray80"),
            font=ctk.CTkFont(size=10)
        )
        self.openai_status_label.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=5)
    
    def create_anthropic_config(self, parent, start_row):
        """Create Anthropic configuration section."""
        row = start_row
        
        # Header
        ctk.CTkLabel(
            parent,
            text="🧠 Anthropic Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
        row += 1
        
        # API Key
        ctk.CTkLabel(parent, text="API Key:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.anthropic_key_entry = ctk.CTkEntry(
            parent,
            placeholder_text="sk-ant-...",
            show="*",
            width=300
        )
        self.anthropic_key_entry.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Model
        ctk.CTkLabel(parent, text="Model:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.anthropic_model_var = ctk.StringVar(value="claude-3-sonnet-20240229")
        self.anthropic_model_menu = ctk.CTkOptionMenu(
            parent,
            variable=self.anthropic_model_var,
            values=["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"]
        )
        self.anthropic_model_menu.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Max tokens
        ctk.CTkLabel(parent, text="Max Tokens:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.anthropic_tokens_entry = ctk.CTkEntry(parent, placeholder_text="1000")
        self.anthropic_tokens_entry.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Test connection button
        self.anthropic_test_button = ctk.CTkButton(
            parent,
            text="Test Connection",
            command=lambda: self.test_provider_connection("anthropic"),
            width=120
        )
        self.anthropic_test_button.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=5)
        row += 1
        
        # Status
        self.anthropic_status_label = ctk.CTkLabel(
            parent,
            text="Status: Not configured",
            text_color=("gray60", "gray80"),
            font=ctk.CTkFont(size=10)
        )
        self.anthropic_status_label.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=5)
    
    def create_local_ai_config(self, parent, start_row):
        """Create Local AI configuration section."""
        row = start_row
        
        # Header
        ctk.CTkLabel(
            parent,
            text="🏠 Local AI Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=(10, 5))
        row += 1
        
        # Server URL
        ctk.CTkLabel(parent, text="Server URL:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.local_url_entry = ctk.CTkEntry(
            parent,
            placeholder_text="http://localhost:11434"
        )
        self.local_url_entry.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Model
        ctk.CTkLabel(parent, text="Model:").grid(
            row=row, column=0, sticky="w", padx=(20, 5), pady=5
        )
        self.local_model_entry = ctk.CTkEntry(
            parent,
            placeholder_text="llama2, mistral, etc."
        )
        self.local_model_entry.grid(row=row, column=1, sticky="ew", padx=(5, 5), pady=5)
        row += 1
        
        # Test connection button
        self.local_test_button = ctk.CTkButton(
            parent,
            text="Test Connection",
            command=lambda: self.test_provider_connection("local"),
            width=120
        )
        self.local_test_button.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=5)
        row += 1
        
        # Status
        self.local_status_label = ctk.CTkLabel(
            parent,
            text="Status: Not configured",
            text_color=("gray60", "gray80"),
            font=ctk.CTkFont(size=10)
        )
        self.local_status_label.grid(row=row, column=1, sticky="w", padx=(5, 5), pady=5)
    
    def setup_general_tab(self):
        """Set up the general settings tab."""
        tab = self.notebook.add("General")
        
        # General settings frame
        general_frame = ctk.CTkFrame(tab)
        general_frame.pack(fill="both", expand=True, padx=10, pady=10)
        general_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Cache settings
        ctk.CTkLabel(
            general_frame,
            text="Cache Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        row += 1
        
        # Cache TTL
        ctk.CTkLabel(general_frame, text="Cache TTL (hours):").grid(
            row=row, column=0, sticky="w", padx=(30, 5), pady=5
        )
        self.cache_ttl_entry = ctk.CTkEntry(general_frame, placeholder_text="1")
        self.cache_ttl_entry.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Max history
        ctk.CTkLabel(general_frame, text="Max History:").grid(
            row=row, column=0, sticky="w", padx=(30, 5), pady=5
        )
        self.max_history_entry = ctk.CTkEntry(general_frame, placeholder_text="100")
        self.max_history_entry.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        row += 1
        
        # Clear cache button
        clear_cache_button = ctk.CTkButton(
            general_frame,
            text="Clear Cache",
            command=self.clear_ai_cache,
            width=120
        )
        clear_cache_button.grid(row=row, column=1, sticky="w", padx=(5, 15), pady=15)
        row += 1
        
        # Temperature setting
        ctk.CTkLabel(
            general_frame,
            text="Generation Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        row += 1
        
        ctk.CTkLabel(general_frame, text="Temperature:").grid(
            row=row, column=0, sticky="w", padx=(30, 5), pady=5
        )
        self.temperature_slider = ctk.CTkSlider(
            general_frame,
            from_=0.1,
            to=2.0,
            number_of_steps=19
        )
        self.temperature_slider.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=5)
        
        self.temperature_label = ctk.CTkLabel(
            general_frame,
            text="0.7",
            text_color=("gray60", "gray80")
        )
        self.temperature_label.grid(row=row+1, column=1, sticky="w", padx=(5, 15), pady=(0, 5))
        
        self.temperature_slider.configure(command=self.on_temperature_changed)
    
    def setup_usage_tab(self):
        """Set up the usage statistics tab."""
        tab = self.notebook.add("Usage")
        
        # Usage frame
        usage_frame = ctk.CTkFrame(tab)
        usage_frame.pack(fill="both", expand=True, padx=10, pady=10)
        usage_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        ctk.CTkLabel(
            usage_frame,
            text="📊 Usage Statistics",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Usage stats text
        self.usage_text = ctk.CTkTextbox(
            usage_frame,
            height=300,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.usage_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Refresh stats button
        refresh_button = ctk.CTkButton(
            usage_frame,
            text="🔄 Refresh Stats",
            command=self.refresh_usage_stats,
            width=120
        )
        refresh_button.pack(pady=(0, 15))
        
        # Load initial stats
        self.refresh_usage_stats()
    
    def setup_advanced_tab(self):
        """Set up the advanced settings tab."""
        tab = self.notebook.add("Advanced")
        
        # Advanced frame
        advanced_frame = ctk.CTkScrollableFrame(tab)
        advanced_frame.pack(fill="both", expand=True, padx=10, pady=10)
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Import/Export settings
        ctk.CTkLabel(
            advanced_frame,
            text="Settings Management",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=row, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        row += 1
        
        # Export button
        export_button = ctk.CTkButton(
            advanced_frame,
            text="Export Settings",
            command=self.export_settings,
            width=120
        )
        export_button.grid(row=row, column=0, sticky="w", padx=(30, 5), pady=5)
        
        # Import button
        import_button = ctk.CTkButton(
            advanced_frame,
            text="Import Settings",
            command=self.import_settings,
            width=120
        )
        import_button.grid(row=row, column=1, sticky="w", padx=(5, 15), pady=5)
        row += 1
        
        # Reset button
        reset_button = ctk.CTkButton(
            advanced_frame,
            text="Reset to Defaults",
            command=self.reset_to_defaults,
            width=120,
            fg_color=("red", "darkred")
        )
        reset_button.grid(row=row, column=0, sticky="w", padx=(30, 5), pady=15)
    
    def load_current_settings(self):
        """Load current AI service settings."""
        if hasattr(self.app, 'ai_service') and self.app.ai_service:
            try:
                self.current_settings = self.app.ai_service.export_settings()
            except Exception as e:
                print(f"Error loading AI settings: {e}")
                self.current_settings = {}
        else:
            self.current_settings = {}
        
        # Apply settings to UI
        self.apply_settings_to_ui()
    
    def apply_settings_to_ui(self):
        """Apply loaded settings to the UI controls."""
        # Set default provider
        default_provider = self.current_settings.get("default_provider", "mock")
        self.default_provider_var.set(default_provider)
        
        # Provider configs
        provider_configs = self.current_settings.get("provider_configs", {})
        
        # OpenAI settings
        openai_config = provider_configs.get("openai", {})
        if "api_key" in openai_config:
            self.openai_key_entry.insert(0, openai_config["api_key"])
        if "model" in openai_config:
            self.openai_model_var.set(openai_config["model"])
        if "max_tokens" in openai_config:
            self.openai_tokens_entry.insert(0, str(openai_config["max_tokens"]))
        
        # Anthropic settings
        anthropic_config = provider_configs.get("anthropic", {})
        if "api_key" in anthropic_config:
            self.anthropic_key_entry.insert(0, anthropic_config["api_key"])
        if "model" in anthropic_config:
            self.anthropic_model_var.set(anthropic_config["model"])
        if "max_tokens" in anthropic_config:
            self.anthropic_tokens_entry.insert(0, str(anthropic_config["max_tokens"]))
        
        # Local AI settings
        local_config = provider_configs.get("local", {})
        if "base_url" in local_config:
            self.local_url_entry.insert(0, local_config["base_url"])
        if "model" in local_config:
            self.local_model_entry.insert(0, local_config["model"])
        
        # General settings
        cache_ttl = self.current_settings.get("cache_ttl", 3600) // 3600  # Convert to hours
        self.cache_ttl_entry.insert(0, str(cache_ttl))
        
        max_history = self.current_settings.get("max_history", 100)
        self.max_history_entry.insert(0, str(max_history))
        
        # Temperature (default 0.7)
        temperature = 0.7  # Default temperature
        self.temperature_slider.set(temperature)
        self.temperature_label.configure(text=str(temperature))
    
    def create_buttons(self):
        """Create the dialog buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Apply button
        apply_button = ctk.CTkButton(
            button_frame,
            text="Apply Settings",
            command=self.apply_settings,
            width=120,
            fg_color=("#4CAF50", "#45A049"),
            hover_color=("#45A049", "#3E8E41")
        )
        apply_button.grid(row=0, column=0, padx=(0, 10))
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=100
        )
        cancel_button.grid(row=0, column=2)
    
    def on_default_provider_changed(self, provider: str):
        """Handle default provider change."""
        pass  # No immediate action needed
    
    def on_temperature_changed(self, value: float):
        """Handle temperature slider change."""
        self.temperature_label.configure(text=f"{value:.1f}")
    
    def test_provider_connection(self, provider: str):
        """Test connection to an AI provider."""
        # This would test the actual connection
        messagebox.showinfo("Connection Test", f"Testing {provider} connection...\n(Not implemented in this demo)")
    
    def clear_ai_cache(self):
        """Clear the AI service cache."""
        if hasattr(self.app, 'ai_service') and self.app.ai_service:
            self.app.ai_service.clear_cache()
            messagebox.showinfo("Cache Cleared", "AI service cache has been cleared.")
        else:
            messagebox.showwarning("AI Service", "AI service is not available.")
    
    def refresh_usage_stats(self):
        """Refresh the usage statistics display."""
        if hasattr(self.app, 'ai_service') and self.app.ai_service:
            try:
                stats = self.app.ai_service.get_usage_stats()
                
                stats_text = f"""AI Service Usage Statistics

Total Requests: {stats.get('total_requests', 0)}
Successful Requests: {stats.get('successful_requests', 0)}
Success Rate: {stats.get('success_rate', 0):.1%}

Cache Size: {stats.get('cache_size', 0)} entries
Default Provider: {stats.get('default_provider', 'None')}

Available Providers: {', '.join(stats.get('available_providers', []))}

Provider Usage:"""
                
                for provider, count in stats.get('provider_usage', {}).items():
                    stats_text += f"\n  • {provider}: {count} requests"
                
                self.usage_text.delete("1.0", "end")
                self.usage_text.insert("1.0", stats_text)
                
            except Exception as e:
                error_text = f"Error loading usage statistics:\n{str(e)}"
                self.usage_text.delete("1.0", "end")
                self.usage_text.insert("1.0", error_text)
        else:
            self.usage_text.delete("1.0", "end")
            self.usage_text.insert("1.0", "AI service is not available.")
    
    def export_settings(self):
        """Export AI settings to file."""
        file_path = filedialog.asksaveasfilename(
            title="Export AI Settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                settings = self.collect_settings_from_ui()
                with open(file_path, 'w') as f:
                    json.dump(settings, f, indent=2)
                messagebox.showinfo("Export Complete", f"Settings exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export settings:\n{str(e)}")
    
    def import_settings(self):
        """Import AI settings from file."""
        file_path = filedialog.askopenfilename(
            title="Import AI Settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                
                self.current_settings = settings
                self.apply_settings_to_ui()
                messagebox.showinfo("Import Complete", f"Settings imported from:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import settings:\n{str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        response = messagebox.askyesno(
            "Reset Settings",
            "Reset all AI settings to defaults?\n\nThis will clear all API keys and configurations.",
            icon="warning"
        )
        
        if response:
            self.current_settings = {}
            # Clear all UI fields
            self.clear_all_ui_fields()
            # Apply defaults
            self.apply_settings_to_ui()
            messagebox.showinfo("Reset Complete", "All settings have been reset to defaults.")
    
    def clear_all_ui_fields(self):
        """Clear all UI input fields."""
        # Clear entry fields
        for entry in [self.openai_key_entry, self.openai_tokens_entry,
                     self.anthropic_key_entry, self.anthropic_tokens_entry,
                     self.local_url_entry, self.local_model_entry,
                     self.cache_ttl_entry, self.max_history_entry]:
            entry.delete(0, "end")
        
        # Reset dropdowns
        self.default_provider_var.set("mock")
        self.openai_model_var.set("gpt-4")
        self.anthropic_model_var.set("claude-3-sonnet-20240229")
        
        # Reset slider
        self.temperature_slider.set(0.7)
        self.temperature_label.configure(text="0.7")
    
    def collect_settings_from_ui(self) -> Dict[str, Any]:
        """Collect settings from UI controls."""
        settings = {
            "default_provider": self.default_provider_var.get(),
            "provider_configs": {
                "openai": {
                    "api_key": self.openai_key_entry.get(),
                    "model": self.openai_model_var.get(),
                    "max_tokens": int(self.openai_tokens_entry.get() or "1000")
                },
                "anthropic": {
                    "api_key": self.anthropic_key_entry.get(),
                    "model": self.anthropic_model_var.get(),
                    "max_tokens": int(self.anthropic_tokens_entry.get() or "1000")
                },
                "local": {
                    "base_url": self.local_url_entry.get(),
                    "model": self.local_model_entry.get()
                }
            },
            "cache_ttl": int(self.cache_ttl_entry.get() or "1") * 3600,  # Convert to seconds
            "max_history": int(self.max_history_entry.get() or "100"),
            "temperature": self.temperature_slider.get()
        }
        
        return settings
    
    def apply_settings(self):
        """Apply the settings to the AI service."""
        try:
            # Collect settings from UI
            settings = self.collect_settings_from_ui()
            
            # Apply to AI service
            if hasattr(self.app, 'ai_service') and self.app.ai_service:
                self.app.ai_service.import_settings(settings)
                messagebox.showinfo("Settings Applied", "AI settings have been applied successfully.")
            else:
                messagebox.showwarning("AI Service", "AI service is not available.")
            
            # Close dialog
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to apply settings:\n{str(e)}")