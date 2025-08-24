"""Batch AI Operations Dialog for DVGE."""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import Dict, Any, List, Set
import time


class BatchAIDialog(ctk.CTkToplevel):
    """Dialog for batch AI operations on dialogue nodes."""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.selected_nodes = set()
        self.operation_results = []
        self.operation_in_progress = False
        
        # Window configuration
        self.title("Batch AI Operations")
        self.geometry("800x650")
        self.minsize(700, 600)
        self.configure(fg_color=("#F0F0F0", "#2B2B2B"))
        
        # Make modal
        self.transient(app)
        self.grab_set()
        
        # Center on parent
        self.center_on_parent()
        
        # Setup UI
        self.setup_ui()
        
        # Load available nodes
        self.load_nodes()
        
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
        self.grid_rowconfigure(2, weight=1)
        
        # Header
        self.create_header()
        
        # Operation selection
        self.create_operation_section()
        
        # Node selection
        self.create_node_selection_section()
        
        # Results section
        self.create_results_section()
        
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
            text="⚡",
            font=ctk.CTkFont(size=24)
        ).grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Title and description
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=10)
        title_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            title_frame,
            text="Batch AI Operations",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Apply AI improvements to multiple dialogue nodes at once",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray70"),
            anchor="w"
        ).grid(row=1, column=0, sticky="w")
    
    def create_operation_section(self):
        """Create the operation selection section."""
        op_frame = ctk.CTkFrame(self)
        op_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        op_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        ctk.CTkLabel(
            op_frame,
            text="🔧 Select Operation",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))
        
        # Operation selection
        ctk.CTkLabel(op_frame, text="Operation:").grid(
            row=1, column=0, sticky="w", padx=(15, 5), pady=5
        )
        
        self.operation_var = ctk.StringVar(value="Enhance Dialogue")
        self.operation_menu = ctk.CTkOptionMenu(
            op_frame,
            variable=self.operation_var,
            values=[
                "Enhance Dialogue",
                "Fix Grammar & Style", 
                "Add Emotional Subtext",
                "Generate Character Voice",
                "Improve Flow & Pacing",
                "Add Missing Choices"
            ],
            command=self.on_operation_changed
        )
        self.operation_menu.grid(row=1, column=1, sticky="ew", padx=(5, 15), pady=5)
        
        # Operation description
        self.operation_desc = ctk.CTkLabel(
            op_frame,
            text="Improve dialogue quality, clarity, and emotional impact using AI.",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray80"),
            justify="left",
            wraplength=400
        )
        self.operation_desc.grid(row=2, column=1, sticky="w", padx=(5, 15), pady=(0, 15))
    
    def create_node_selection_section(self):
        """Create the node selection section."""
        selection_frame = ctk.CTkFrame(self)
        selection_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_rowconfigure(2, weight=1)
        
        # Section header
        header_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="📝 Select Nodes",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Selection controls
        controls_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        # Select all/none buttons
        ctk.CTkButton(
            controls_frame,
            text="Select All",
            command=self.select_all_nodes,
            width=80,
            height=30
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            controls_frame,
            text="Select None",
            command=self.select_no_nodes,
            width=80,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="Selected Only",
            command=self.select_currently_selected,
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        # Selection count
        self.selection_count_label = ctk.CTkLabel(
            controls_frame,
            text="0 nodes selected",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray80")
        )
        self.selection_count_label.pack(side="right")
        
        # Node list
        self.node_list_frame = ctk.CTkScrollableFrame(selection_frame)
        self.node_list_frame.grid(row=2, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self.node_checkboxes = {}
    
    def create_results_section(self):
        """Create the results section."""
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Section header
        ctk.CTkLabel(
            results_frame,
            text="📊 Operation Results",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Results text
        self.results_text = ctk.CTkTextbox(
            results_frame,
            height=100,
            font=ctk.CTkFont(size=11)
        )
        self.results_text.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.results_text.insert("1.0", "Select nodes and operation, then click 'Run Operation' to begin.")
        self.results_text.configure(state="disabled")
    
    def create_buttons(self):
        """Create the dialog buttons."""
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Run operation button
        self.run_button = ctk.CTkButton(
            button_frame,
            text="⚡ Run Operation",
            command=self.run_batch_operation,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4CAF50", "#45A049"),
            hover_color=("#45A049", "#3E8E41")
        )
        self.run_button.grid(row=0, column=0, padx=(0, 10))
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            width=100,
            height=40
        )
        cancel_button.grid(row=0, column=2)
    
    def load_nodes(self):
        """Load available nodes into the selection list."""
        # Clear existing checkboxes
        for checkbox in self.node_checkboxes.values():
            checkbox.destroy()
        self.node_checkboxes.clear()
        
        # Add nodes with dialogue text
        for node_id, node in self.app.nodes.items():
            if hasattr(node, 'game_data') and node.game_data.get('text', '').strip():
                self.add_node_checkbox(node_id, node)
        
        # Update selection count
        self.update_selection_count()
    
    def add_node_checkbox(self, node_id: str, node: Any):
        """Add a checkbox for a node."""
        # Create checkbox frame
        checkbox_frame = ctk.CTkFrame(self.node_list_frame)
        checkbox_frame.pack(fill="x", padx=5, pady=2)
        checkbox_frame.grid_columnconfigure(1, weight=1)
        
        # Checkbox
        checkbox_var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="",
            variable=checkbox_var,
            command=lambda: self.on_node_selection_changed(node_id, checkbox_var.get())
        )
        checkbox.grid(row=0, column=0, padx=(5, 10), pady=5)
        
        # Node info
        node_text = node.game_data.get('text', '')[:100]
        if len(node_text) == 100:
            node_text += "..."
        
        node_label = ctk.CTkLabel(
            checkbox_frame,
            text=f"Node {node_id}: {node_text}",
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left"
        )
        node_label.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)
        
        # Store checkbox reference
        self.node_checkboxes[node_id] = checkbox
    
    def on_node_selection_changed(self, node_id: str, selected: bool):
        """Handle node selection change."""
        if selected:
            self.selected_nodes.add(node_id)
        else:
            self.selected_nodes.discard(node_id)
        
        self.update_selection_count()
    
    def update_selection_count(self):
        """Update the selection count label."""
        count = len(self.selected_nodes)
        self.selection_count_label.configure(text=f"{count} nodes selected")
        
        # Enable/disable run button
        self.run_button.configure(state="normal" if count > 0 else "disabled")
    
    def select_all_nodes(self):
        """Select all nodes."""
        for node_id, checkbox in self.node_checkboxes.items():
            checkbox.select()
            self.selected_nodes.add(node_id)
        self.update_selection_count()
    
    def select_no_nodes(self):
        """Deselect all nodes."""
        for checkbox in self.node_checkboxes.values():
            checkbox.deselect()
        self.selected_nodes.clear()
        self.update_selection_count()
    
    def select_currently_selected(self):
        """Select only currently selected nodes in the main app."""
        # First clear all selections
        self.select_no_nodes()
        
        # Then select nodes that are currently selected in the app
        for node_id in self.app.selected_node_ids:
            if node_id in self.node_checkboxes:
                self.node_checkboxes[node_id].select()
                self.selected_nodes.add(node_id)
        
        self.update_selection_count()
    
    def on_operation_changed(self, operation: str):
        """Handle operation selection change."""
        descriptions = {
            "Enhance Dialogue": "Improve dialogue quality, clarity, and emotional impact using AI.",
            "Fix Grammar & Style": "Correct grammar, punctuation, and improve writing style consistency.",
            "Add Emotional Subtext": "Add emotional depth and subtext to dialogue for better character expression.",
            "Generate Character Voice": "Ensure each character has a distinct and consistent voice throughout.",
            "Improve Flow & Pacing": "Optimize dialogue flow and pacing for better player engagement.",
            "Add Missing Choices": "Generate appropriate player choice options where they might be missing."
        }
        
        self.operation_desc.configure(text=descriptions.get(operation, ""))
    
    def run_batch_operation(self):
        """Run the batch AI operation."""
        if not self.selected_nodes:
            messagebox.showwarning("No Selection", "Please select at least one node.")
            return
        
        if self.operation_in_progress:
            messagebox.showinfo("Operation in Progress", "Please wait for the current operation to complete.")
            return
        
        # Confirm operation
        operation = self.operation_var.get()
        count = len(self.selected_nodes)
        
        response = messagebox.askyesno(
            "Confirm Batch Operation",
            f"Apply '{operation}' to {count} selected nodes?\n\n" + 
            "This operation may take several minutes and will modify your nodes. " +
            "You can undo these changes afterward.",
            icon="question"
        )
        
        if not response:
            return
        
        # Start operation
        self.operation_in_progress = True
        self.run_button.configure(text="⚡ Running...", state="disabled")
        
        # Clear results
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", f"Starting {operation} on {count} nodes...\n\n")
        self.results_text.configure(state="disabled")
        
        # Run in background
        def operation_worker():
            try:
                self._run_batch_operation()
                self.after(0, self._on_operation_complete)
            except Exception as e:
                self.after(0, lambda: self._on_operation_error(str(e)))
        
        thread = threading.Thread(target=operation_worker, daemon=True)
        thread.start()
    
    def _run_batch_operation(self):
        """Run the actual batch operation."""
        if not hasattr(self.app, 'ai_service') or not self.app.ai_service:
            raise Exception("AI service is not available")
        
        if not self.app.ai_service.is_enhanced_ai_available():
            raise Exception("Enhanced AI features are not available")
        
        # Get batch operations system
        batch_system = self.app.ai_service.enhanced_systems.batch_operations
        if not batch_system:
            raise Exception("Batch operations system not available")
        
        # Prepare operation parameters
        operation_type = self.operation_var.get().lower().replace(" ", "_").replace("&", "and")
        
        # Save state for undo
        self.app.state_manager.save_state(f"Batch AI: {self.operation_var.get()}")
        
        # Run batch operation
        self.operation_results = []
        total_nodes = len(self.selected_nodes)
        
        for i, node_id in enumerate(self.selected_nodes, 1):
            if node_id in self.app.nodes:
                node = self.app.nodes[node_id]
                
                # Update progress
                progress_msg = f"Processing node {i}/{total_nodes}: {node_id}\n"
                self.after(0, lambda msg=progress_msg: self._update_progress(msg))
                
                try:
                    # Apply operation based on type
                    result = self._apply_operation_to_node(batch_system, operation_type, node_id, node)
                    self.operation_results.append(result)
                    
                    # Brief delay to prevent overwhelming the AI service
                    time.sleep(0.5)
                    
                except Exception as e:
                    error_result = {
                        'node_id': node_id,
                        'success': False,
                        'error': str(e)
                    }
                    self.operation_results.append(error_result)
    
    def _apply_operation_to_node(self, batch_system, operation_type: str, node_id: str, node: Any) -> Dict[str, Any]:
        """Apply the operation to a single node."""
        if operation_type == "enhance_dialogue":
            return batch_system.enhance_dialogue_batch([node_id])[0]
        elif operation_type == "fix_grammar_and_style":
            return batch_system.fix_grammar_batch([node_id])[0]
        elif operation_type == "add_emotional_subtext":
            return batch_system.add_emotional_subtext_batch([node_id])[0]
        elif operation_type == "generate_character_voice":
            return batch_system.improve_character_voice_batch([node_id])[0]
        elif operation_type == "improve_flow_and_pacing":
            return batch_system.improve_pacing_batch([node_id])[0]
        elif operation_type == "add_missing_choices":
            return batch_system.generate_choices_batch([node_id])[0]
        else:
            raise Exception(f"Unknown operation type: {operation_type}")
    
    def _update_progress(self, message: str):
        """Update progress in results text."""
        self.results_text.configure(state="normal")
        self.results_text.insert("end", message)
        self.results_text.see("end")
        self.results_text.configure(state="disabled")
        self.update()
    
    def _on_operation_complete(self):
        """Handle completed operation."""
        self.operation_in_progress = False
        self.run_button.configure(text="⚡ Run Operation", state="normal")
        
        # Display results
        self._display_operation_results()
        
        # Refresh UI
        self.app.properties_panel.update_properties_panel()
        self.app.canvas_manager.redraw_all_nodes()
        
        messagebox.showinfo(
            "Operation Complete",
            f"Batch operation completed!\n\n" + 
            f"Processed {len(self.operation_results)} nodes.\n" +
            "Check the results section for details."
        )
    
    def _on_operation_error(self, error_message: str):
        """Handle operation error."""
        self.operation_in_progress = False
        self.run_button.configure(text="⚡ Run Operation", state="normal")
        
        error_msg = f"\n❌ Operation failed: {error_message}\n"
        self.results_text.configure(state="normal")
        self.results_text.insert("end", error_msg)
        self.results_text.configure(state="disabled")
        
        messagebox.showerror("Operation Error", error_message)
    
    def _display_operation_results(self):
        """Display the operation results."""
        if not self.operation_results:
            return
        
        self.results_text.configure(state="normal")
        self.results_text.insert("end", "\n" + "="*50 + "\n")
        self.results_text.insert("end", "OPERATION RESULTS:\n\n")
        
        success_count = sum(1 for r in self.operation_results if r.get('success', False))
        error_count = len(self.operation_results) - success_count
        
        self.results_text.insert("end", f"✅ Successful: {success_count}\n")
        self.results_text.insert("end", f"❌ Failed: {error_count}\n\n")
        
        # Show detailed results
        for result in self.operation_results:
            node_id = result.get('node_id', 'Unknown')
            if result.get('success', False):
                self.results_text.insert("end", f"✅ Node {node_id}: Enhanced successfully\n")
            else:
                error = result.get('error', 'Unknown error')
                self.results_text.insert("end", f"❌ Node {node_id}: {error}\n")
        
        self.results_text.see("end")
        self.results_text.configure(state="disabled")