# dvge/ui/sidebar.py
import tkinter as tk
import customtkinter as ctk
from ..theme import *
from .properties_panel import PropertiesPanel
from .project_panel import ProjectPanel

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLOR_PRIMARY_FRAME)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self, fg_color=COLOR_SECONDARY_FRAME,
                                       segmented_button_fg_color=COLOR_PRIMARY_FRAME,
                                       segmented_button_selected_color=COLOR_ACCENT,
                                       segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
                                       segmented_button_unselected_hover_color=COLOR_SECONDARY_FRAME)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_view.add("Inspector")
        self.tab_view.add("Project")

        self.properties_panel = PropertiesPanel(self.tab_view.tab("Inspector"), self.app)
        self.properties_panel.pack(fill="both", expand=True)

        self.project_panel = ProjectPanel(self.tab_view.tab("Project"), self.app)
        self.project_panel.pack(fill="both", expand=True)

    def update_all_panels(self):
        self.properties_panel.update_all_panels()
        self.project_panel.update_all_panels()

    def update_properties_panel(self):
        self.properties_panel.update_properties_panel()