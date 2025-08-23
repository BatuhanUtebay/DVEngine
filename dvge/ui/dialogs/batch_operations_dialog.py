"""Batch Operations Dialog for DVGE - Fixed Version."""

import customtkinter as ctk
from tkinter import messagebox, simpledialog
from typing import Dict, Any


class BatchOperationsDialog(ctk.CTkToplevel):
    """Dialog for configuring and executing batch operations on nodes."""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        
        self.app = app
        self.result = None
        
        # Import here to avoid circular imports
        from ...core.batch_operations import BatchOperationManager
        self.batch_manager = BatchOperationManager(app)
        
        self.title("Batch Operations")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Center the dialog
        self.center_window()
        
        self.setup_ui()
        
    def center_window(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Set up the dialog UI."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Batch Operations", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # Quick Operations tab
        self.setup_quick_operations_tab()
        
        # Advanced Operations tab  
        self.setup_advanced_operations_tab()
        
        # Results tab
        self.setup_results_tab()
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.close_dialog
        )
        close_button.pack(side="right", padx=(10, 0))
        
        help_button = ctk.CTkButton(
            button_frame,
            text="Help",
            command=self.show_help
        )
        help_button.pack(side="right")
    
    def setup_quick_operations_tab(self):
        """Set up the quick operations tab."""
        tab = self.notebook.add("Quick Operations")
        
        # Description
        desc_label = ctk.CTkLabel(
            tab,
            text="Common batch operations with preset configurations",
            font=ctk.CTkFont(size=14)
        )
        desc_label.pack(pady=(10, 20))
        
        # Quick operation buttons
        operations = [
            ("Find & Replace Text", self.quick_find_replace),
            ("Change Node Colors", self.quick_change_colors),
            ("Fix Empty Dialogue", self.quick_fix_empty),
            ("Remove Broken Connections", self.quick_remove_broken),
            ("Normalize NPC Names", self.quick_normalize_npcs),
            ("Validate All Nodes", self.quick_validate),
            ("Find Orphaned Nodes", self.quick_find_orphaned),
            ("Auto-Arrange by Chapter", self.quick_auto_arrange)
        ]
        
        # Create container frame for buttons
        buttons_frame = ctk.CTkFrame(tab)
        buttons_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create grid of operation buttons
        for i, (name, command) in enumerate(operations):
            row = i // 2
            col = i % 2
            
            button = ctk.CTkButton(
                buttons_frame,
                text=name,
                command=command,
                width=300,
                height=40
            )
            button.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        # Configure grid weights
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
    
    def setup_advanced_operations_tab(self):
        """Set up the advanced operations tab."""
        tab = self.notebook.add("Advanced")
        
        # Filter selection
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Node Filter:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.filter_var = ctk.StringVar(value="all")
        filter_options = ["all", "selected", "by_type", "by_npc", "by_text", "by_theme", "by_chapter", "by_color", "orphaned", "dead_end"]
        
        self.filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            variable=self.filter_var,
            values=filter_options,
            command=self.on_filter_changed
        )
        self.filter_dropdown.pack(anchor="w", padx=10, pady=10)
        
        # Filter parameters frame (dynamic content)
        self.filter_params_frame = ctk.CTkFrame(filter_frame)
        self.filter_params_frame.pack(fill="x", padx=10, pady=10)
        
        # Operation selection
        operation_frame = ctk.CTkFrame(tab)
        operation_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(operation_frame, text="Operation:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 0))
        
        operations = list(self.batch_manager.get_available_operations().keys())
        self.operation_var = ctk.StringVar(value=operations[0] if operations else "")
        
        self.operation_dropdown = ctk.CTkOptionMenu(
            operation_frame,
            variable=self.operation_var,
            values=operations,
            command=self.on_operation_changed
        )
        self.operation_dropdown.pack(anchor="w", padx=10, pady=10)
        
        # Operation parameters frame (dynamic content)
        self.operation_params_frame = ctk.CTkFrame(operation_frame)
        self.operation_params_frame.pack(fill="x", padx=10, pady=10)
        
        # Execute button
        execute_button = ctk.CTkButton(
            tab,
            text="Execute Operation",
            command=self.execute_advanced_operation,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50
        )
        execute_button.pack(pady=20)
        
        # Initialize dynamic content
        self.on_filter_changed("all")
        self.on_operation_changed(operations[0] if operations else "")
    
    def setup_results_tab(self):
        """Set up the results tab."""
        tab = self.notebook.add("Results")
        
        # Results text area
        self.results_text = ctk.CTkTextbox(tab)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Clear results button
        clear_button = ctk.CTkButton(
            tab,
            text="Clear Results",
            command=self.clear_results
        )
        clear_button.pack(pady=10)
        
        # Load any existing history
        self.load_results_history()
    
    def on_filter_changed(self, selection):
        """Handle filter selection change."""
        # Clear existing params
        for widget in self.filter_params_frame.winfo_children():
            widget.destroy()
        
        # Add specific parameter inputs based on filter
        if selection == "by_type":
            ctk.CTkLabel(self.filter_params_frame, text="Node Type:").pack(anchor="w", padx=5, pady=2)
            self.type_var = ctk.StringVar(value="dialogue")
            ctk.CTkOptionMenu(
                self.filter_params_frame,
                variable=self.type_var,
                values=["dialogue", "combat", "dice_roll", "qte", "script"]
            ).pack(anchor="w", padx=5, pady=2)
            
        elif selection == "by_npc":
            ctk.CTkLabel(self.filter_params_frame, text="NPC Name:").pack(anchor="w", padx=5, pady=2)
            self.npc_var = ctk.StringVar()
            ctk.CTkEntry(self.filter_params_frame, textvariable=self.npc_var).pack(fill="x", padx=5, pady=2)
            
            self.npc_exact_var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                self.filter_params_frame,
                text="Exact match",
                variable=self.npc_exact_var
            ).pack(anchor="w", padx=5, pady=2)
            
        elif selection == "by_text":
            ctk.CTkLabel(self.filter_params_frame, text="Search Text:").pack(anchor="w", padx=5, pady=2)
            self.search_text_var = ctk.StringVar()
            ctk.CTkEntry(self.filter_params_frame, textvariable=self.search_text_var).pack(fill="x", padx=5, pady=2)
            
            self.case_sensitive_var = ctk.BooleanVar()
            ctk.CTkCheckBox(
                self.filter_params_frame,
                text="Case sensitive",
                variable=self.case_sensitive_var
            ).pack(anchor="w", padx=5, pady=2)
            
        elif selection in ["by_theme", "by_chapter", "by_color"]:
            label_text = selection.replace("by_", "").title() + ":"
            ctk.CTkLabel(self.filter_params_frame, text=label_text).pack(anchor="w", padx=5, pady=2)
            setattr(self, f"{selection.replace('by_', '')}_var", ctk.StringVar())
            ctk.CTkEntry(
                self.filter_params_frame,
                textvariable=getattr(self, f"{selection.replace('by_', '')}_var")
            ).pack(fill="x", padx=5, pady=2)
    
    def on_operation_changed(self, selection):
        """Handle operation selection change."""
        # Clear existing params
        for widget in self.operation_params_frame.winfo_children():
            widget.destroy()
        
        # Add specific parameter inputs based on operation
        if "text" in selection:
            if "find_replace" in selection:
                ctk.CTkLabel(self.operation_params_frame, text="Find Text:").pack(anchor="w", padx=5, pady=2)
                self.find_text_var = ctk.StringVar()
                ctk.CTkEntry(self.operation_params_frame, textvariable=self.find_text_var).pack(fill="x", padx=5, pady=2)
                
                ctk.CTkLabel(self.operation_params_frame, text="Replace With:").pack(anchor="w", padx=5, pady=2)
                self.replace_text_var = ctk.StringVar()
                ctk.CTkEntry(self.operation_params_frame, textvariable=self.replace_text_var).pack(fill="x", padx=5, pady=2)
                
                self.replace_case_sensitive_var = ctk.BooleanVar()
                ctk.CTkCheckBox(
                    self.operation_params_frame,
                    text="Case sensitive",
                    variable=self.replace_case_sensitive_var
                ).pack(anchor="w", padx=5, pady=2)
                
            elif "append" in selection or "prepend" in selection:
                label = "Append Text:" if "append" in selection else "Prepend Text:"
                ctk.CTkLabel(self.operation_params_frame, text=label).pack(anchor="w", padx=5, pady=2)
                self.text_to_add_var = ctk.StringVar()
                ctk.CTkEntry(self.operation_params_frame, textvariable=self.text_to_add_var).pack(fill="x", padx=5, pady=2)
                
        elif "change_color" in selection:
            ctk.CTkLabel(self.operation_params_frame, text="New Color:").pack(anchor="w", padx=5, pady=2)
            self.new_color_var = ctk.StringVar(value="#FF0000")
            ctk.CTkEntry(self.operation_params_frame, textvariable=self.new_color_var).pack(fill="x", padx=5, pady=2)
            
        elif "change_theme" in selection:
            ctk.CTkLabel(self.operation_params_frame, text="New Theme:").pack(anchor="w", padx=5, pady=2)
            self.new_theme_var = ctk.StringVar()
            ctk.CTkOptionMenu(
                self.operation_params_frame,
                variable=self.new_theme_var,
                values=["forest", "dungeon", "tavern", "castle", "city", "desert"]
            ).pack(anchor="w", padx=5, pady=2)
            
        elif "change_chapter" in selection:
            ctk.CTkLabel(self.operation_params_frame, text="New Chapter:").pack(anchor="w", padx=5, pady=2)
            self.new_chapter_var = ctk.StringVar()
            ctk.CTkEntry(self.operation_params_frame, textvariable=self.new_chapter_var).pack(fill="x", padx=5, pady=2)
            
        elif "change_npc" in selection:
            ctk.CTkLabel(self.operation_params_frame, text="New NPC:").pack(anchor="w", padx=5, pady=2)
            self.new_npc_var = ctk.StringVar()
            ctk.CTkEntry(self.operation_params_frame, textvariable=self.new_npc_var).pack(fill="x", padx=5, pady=2)
            
        elif "fix_empty_text" in selection:
            ctk.CTkLabel(self.operation_params_frame, text="Placeholder Text:").pack(anchor="w", padx=5, pady=2)
            self.placeholder_var = ctk.StringVar(value="[Empty dialogue - please add content]")
            ctk.CTkEntry(self.operation_params_frame, textvariable=self.placeholder_var).pack(fill="x", padx=5, pady=2)
    
    # Quick operation methods
    def quick_find_replace(self):
        """Quick find and replace dialog."""
        find_text = simpledialog.askstring("Find Text", "Enter text to find:")
        if not find_text:
            return
            
        replace_text = simpledialog.askstring("Replace Text", "Enter replacement text:") or ""
        
        result = self.batch_manager.execute_operation(
            "find_replace_text",
            "all",
            find_text=find_text,
            replace_text=replace_text,
            case_sensitive=False
        )
        
        self.display_result(result)
        self.notebook.set("Results")
    
    def quick_change_colors(self):
        """Quick color change dialog."""
        if not self.app.selected_node_ids:
            messagebox.showwarning("No Selection", "Please select nodes first.")
            return
            
        new_color = simpledialog.askstring("Change Color", "Enter new color (hex format, e.g., #FF0000):") or "#FF0000"
        
        result = self.batch_manager.execute_operation(
            "change_color",
            "selected", 
            new_color=new_color
        )
        
        self.display_result(result)
        self.notebook.set("Results")
        
        # Redraw nodes to show color changes
        if hasattr(self.app, 'canvas_manager'):
            self.app.canvas_manager.redraw_all_nodes()
    
    def quick_fix_empty(self):
        """Quick fix empty dialogue."""
        result = self.batch_manager.execute_operation(
            "fix_empty_text",
            "all"
        )
        
        self.display_result(result)
        self.notebook.set("Results")
    
    def quick_remove_broken(self):
        """Quick remove broken connections."""
        result = self.batch_manager.execute_operation(
            "remove_broken_connections",
            "all"
        )
        
        self.display_result(result)
        self.notebook.set("Results")
    
    def quick_normalize_npcs(self):
        """Quick normalize NPC names."""
        result = self.batch_manager.execute_operation(
            "normalize_npc_names",
            "all"
        )
        
        self.display_result(result)
        self.notebook.set("Results")
    
    def quick_validate(self):
        """Quick validate all nodes."""
        result = self.batch_manager.execute_operation(
            "validate_nodes",
            "all"
        )
        
        self.display_result(result)
        self.notebook.set("Results")
    
    def quick_find_orphaned(self):
        """Quick find orphaned nodes."""
        result = self.batch_manager.execute_operation(
            "validate_nodes",
            "orphaned"
        )
        
        self.display_result(result)
        self.notebook.set("Results")
    
    def quick_auto_arrange(self):
        """Quick auto-arrange by chapter."""
        result = self.batch_manager.execute_operation(
            "auto_arrange_by_chapter",
            "all"
        )
        
        self.display_result(result)
        self.notebook.set("Results")
        
        # Redraw nodes to show position changes
        if hasattr(self.app, 'canvas_manager'):
            self.app.canvas_manager.redraw_all_nodes()
    
    def execute_advanced_operation(self):
        """Execute the configured advanced operation."""
        try:
            # Get filter parameters
            filter_params = self.get_filter_parameters()
            
            # Get operation parameters
            operation_params = self.get_operation_parameters()
            
            # Execute operation
            result = self.batch_manager.execute_operation(
                self.operation_var.get(),
                self.filter_var.get(),
                filter_params=filter_params,
                **operation_params
            )
            
            self.display_result(result)
            self.notebook.set("Results")
            
            # Redraw if needed
            if hasattr(self.app, 'canvas_manager') and any(
                op in self.operation_var.get() 
                for op in ['color', 'arrange', 'theme']
            ):
                self.app.canvas_manager.redraw_all_nodes()
                
        except Exception as e:
            messagebox.showerror("Operation Error", f"Failed to execute operation:\n{str(e)}")
    
    def get_filter_parameters(self) -> Dict[str, Any]:
        """Get filter parameters from UI."""
        filter_type = self.filter_var.get()
        params = {}
        
        if filter_type == "by_type" and hasattr(self, 'type_var'):
            params['node_type'] = self.type_var.get()
        elif filter_type == "by_npc" and hasattr(self, 'npc_var'):
            params['npc_name'] = self.npc_var.get()
            params['exact_match'] = getattr(self, 'npc_exact_var', ctk.BooleanVar()).get()
        elif filter_type == "by_text" and hasattr(self, 'search_text_var'):
            params['search_text'] = self.search_text_var.get()
            params['case_sensitive'] = getattr(self, 'case_sensitive_var', ctk.BooleanVar()).get()
        elif filter_type == "by_theme" and hasattr(self, 'theme_var'):
            params['theme'] = self.theme_var.get()
        elif filter_type == "by_chapter" and hasattr(self, 'chapter_var'):
            params['chapter'] = self.chapter_var.get()
        elif filter_type == "by_color" and hasattr(self, 'color_var'):
            params['color'] = self.color_var.get()
            
        return params
    
    def get_operation_parameters(self) -> Dict[str, Any]:
        """Get operation parameters from UI."""
        operation = self.operation_var.get()
        params = {}
        
        if "find_replace" in operation:
            params['find_text'] = getattr(self, 'find_text_var', ctk.StringVar()).get()
            params['replace_text'] = getattr(self, 'replace_text_var', ctk.StringVar()).get()
            params['case_sensitive'] = getattr(self, 'replace_case_sensitive_var', ctk.BooleanVar()).get()
        elif "append" in operation and hasattr(self, 'text_to_add_var'):
            params['append_text'] = self.text_to_add_var.get()
        elif "prepend" in operation and hasattr(self, 'text_to_add_var'):
            params['prepend_text'] = self.text_to_add_var.get()
        elif "change_color" in operation and hasattr(self, 'new_color_var'):
            params['new_color'] = self.new_color_var.get()
        elif "change_theme" in operation and hasattr(self, 'new_theme_var'):
            params['new_theme'] = self.new_theme_var.get()
        elif "change_chapter" in operation and hasattr(self, 'new_chapter_var'):
            params['new_chapter'] = self.new_chapter_var.get()
        elif "change_npc" in operation and hasattr(self, 'new_npc_var'):
            params['new_npc'] = self.new_npc_var.get()
        elif "fix_empty_text" in operation and hasattr(self, 'placeholder_var'):
            params['placeholder_text'] = self.placeholder_var.get()
            
        return params
    
    def display_result(self, result: Dict[str, Any]):
        """Display operation result in the results tab."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        result_text = f"\n[{timestamp}] {result['operation'].upper()}\n"
        result_text += f"Total nodes: {result['total']}, Successful: {result['successful']}, Failed: {result['failed']}\n"
        
        if result.get('message'):
            result_text += f"Message: {result['message']}\n"
        
        # Show detailed results for failed operations
        if result['failed'] > 0:
            failed_nodes = [r for r in result['results'] if not r['success']]
            result_text += "Failed nodes:\n"
            for failed in failed_nodes[:5]:  # Show first 5 failures
                result_text += f"  - {failed['node_id']}: {failed['error']}\n"
            if len(failed_nodes) > 5:
                result_text += f"  ... and {len(failed_nodes) - 5} more\n"
        
        result_text += "-" * 50 + "\n"
        
        # Append to results text
        current_text = self.results_text.get("1.0", "end")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", result_text + current_text)
    
    def load_results_history(self):
        """Load previous operation results."""
        if hasattr(self, 'batch_manager'):
            history = self.batch_manager.get_operation_history()
            for result in reversed(history[-10:]):  # Show last 10 operations
                self.display_result(result)
    
    def clear_results(self):
        """Clear the results display."""
        self.results_text.delete("1.0", "end")
        if hasattr(self, 'batch_manager'):
            self.batch_manager.clear_history()
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
Batch Operations Help

Quick Operations:
• Pre-configured common tasks
• One-click execution
• Automatic parameter selection

Advanced Operations:
• Full control over filters and parameters
• Custom configurations
• Complex operation chains

Filters:
• all: All nodes in the project
• selected: Currently selected nodes
• by_type: Filter by node type
• by_npc: Filter by NPC speaker name
• by_text: Filter by dialogue content
• by_theme/chapter/color: Filter by attributes
• orphaned: Nodes with no incoming connections
• dead_end: Nodes with no outgoing connections

Operations:
• Text operations: Find/replace, append, prepend
• Styling: Change colors, themes, chapters
• Validation: Check for issues, fix problems
• Organization: Auto-arrange, normalize names
• Connections: Remove broken links

Tips:
• Always backup your project before batch operations
• Use validation operations to check project health
• Start with small test operations before large changes
• Check the Results tab for detailed feedback
"""
        
        messagebox.showinfo("Batch Operations Help", help_text)
    
    def close_dialog(self):
        """Close the dialog."""
        self.destroy()