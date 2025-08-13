# dvge/ui/dialogs/search_dialog.py

"""Search dialog for finding nodes."""

import tkinter as tk
import customtkinter as ctk


class SearchDialog(ctk.CTkToplevel):
    """A Toplevel window for searching nodes."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Find Node")
        self.geometry("400x300")
        self.attributes("-topmost", True)

        self._setup_layout()
        self._create_widgets()

    def _setup_layout(self):
        """Sets up the dialog layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_widgets(self):
        """Creates all widgets for the search dialog."""
        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)

        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search by ID, NPC, or Text..."
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<Return>", self._perform_search)
        self.search_entry.focus()

        # Search button
        ctk.CTkButton(
            search_frame, text="Search", command=self._perform_search
        ).grid(row=0, column=1)

        # Results listbox
        self.results_listbox = tk.Listbox(
            self, 
            bg="#2B2B2B", 
            fg="white", 
            selectbackground="#1F6AA5", 
            highlightthickness=0, 
            borderwidth=0
        )
        self.results_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.results_listbox.bind("<Double-Button-1>", self._go_to_result)

    def _perform_search(self, event=None):
        """Performs the search and updates results."""
        search_term = self.search_entry.get().lower()
        self.results_listbox.delete(0, tk.END)
        
        if not search_term:
            return

        # Search through all nodes
        for node_id, node in self.parent.nodes.items():
            # Check if search term matches ID, NPC name, or dialogue text
            if (search_term in node.id.lower() or
                search_term in node.npc.lower() or
                search_term in node.text.lower()):
                
                # Display format: "node_id (NPC Name)"
                display_text = f"{node.id} ({node.npc})"
                self.results_listbox.insert(tk.END, display_text)

    def _go_to_result(self, event=None):
        """Navigates to the selected search result."""
        selection = self.results_listbox.curselection()
        if not selection:
            return
        
        # Extract node ID from the display text
        selected_text = self.results_listbox.get(selection[0])
        node_id = selected_text.split(" ")[0]
        
        # Pan to the node and close dialog
        self.parent.canvas_manager.pan_to_node(node_id)
        self.destroy()