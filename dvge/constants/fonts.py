# dvge/constants/fonts.py

"""Font constants for the DVGE application."""

# --- FONT DEFINITIONS ---
try:
    FONT_FAMILY = "Roboto"
except:
    FONT_FAMILY = "Segoe UI"

FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_NPC = (FONT_FAMILY, 13, "bold")
FONT_DIALOGUE = (FONT_FAMILY, 11)
FONT_OPTION = (FONT_FAMILY, 11, "italic")
FONT_ADD_BUTTON = (FONT_FAMILY, 11, "bold")
FONT_PROPERTIES_LABEL = (FONT_FAMILY, 12, "bold")
FONT_PROPERTIES_ENTRY = (FONT_FAMILY, 11)
FONT_ICON = ("Segoe UI Symbol", 14)