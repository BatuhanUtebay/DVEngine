# dvge/ui/search_dialog.py
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by ID, NPC, or Text...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.search_entry.bind("<Return>", self.perform_search)
        self.search_entry.focus()

        ctk.CTkButton(search_frame, text="Search", command=self.perform_search).grid(row=0, column=1)

        self.results_listbox = tk.Listbox(self, bg="#2B2B2B", fg="white", selectbackground="#1F6AA5", highlightthickness=0, borderwidth=0)
        self.results_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.results_listbox.bind("<Double-Button-1>", self.go_to_result)

    def perform_search(self, event=None):
        search_term = self.search_entry.get().lower()
        self.results_listbox.delete(0, tk.END)
        if not search_term: return

        for node_id, node in self.parent.nodes.items():
            if (search_term in node.id.lower() or
                search_term in node.npc.lower() or
                search_term in node.text.lower()):
                self.results_listbox.insert(tk.END, f"{node.id} ({node.npc})")

    def go_to_result(self, event=None):
        selection = self.results_listbox.curselection()
        if not selection: return
        node_id = self.results_listbox.get(selection[0]).split(" ")[0]
        self.parent.canvas_manager.pan_to_node(node_id)
        self.destroy()
