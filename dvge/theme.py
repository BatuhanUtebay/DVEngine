# dvge/theme.py

# --- COLOR PALETTE ---
COLOR_BACKGROUND = "#1E1E1E"          # Dark grey, almost black
COLOR_PRIMARY_FRAME = "#2D2D30"       # Slightly lighter dark grey
COLOR_SECONDARY_FRAME = "#3B3B3E"     # Medium dark grey
COLOR_CANVAS_BACKGROUND = "#191919"   # Very dark grey for the node canvas
COLOR_GRID_LINES = "#2A2A2A"          # Subtle grid lines

COLOR_TEXT = "#EAEAEA"                # Off-white for primary text
COLOR_TEXT_MUTED = "#A0A0A0"           # Grey for secondary/placeholder text
COLOR_TEXT_DISABLED = "#6A6A6A"        # Darker grey for disabled elements

COLOR_ACCENT = "#4A90E2"              # A vibrant blue for selection and interaction
COLOR_ACCENT_HOVER = "#63A3E9"         # Lighter blue for hover states
COLOR_ACCENT_DARK = "#2C5E8E"          # A darker blue for pressed states

COLOR_SUCCESS = "#5DBB63"              # Green for success notifications
COLOR_WARNING = "#F5A623"              # Orange for warnings
COLOR_ERROR = "#D0021B"                # Red for errors and deletion

NODE_DEFAULT_COLOR = "#333333"
NODE_INTRO_COLOR = "#2C5E8E"
NODE_COMBAT_COLOR = "#8B0000"
NODE_SELECTED_OUTLINE_COLOR = COLOR_ACCENT

# --- FONT DEFINITIONS ---
FONT_FAMILY = "Roboto"  # A clean, modern sans-serif font
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 16, "bold")
FONT_BODY = (FONT_FAMILY, 12)
FONT_BODY_BOLD = (FONT_FAMILY, 12, "bold")
FONT_SMALL = (FONT_FAMILY, 10, "italic")
FONT_ICON = ("Segoe UI Symbol", 14)

# --- UI DIMENSIONS & STYLES ---
NODE_WIDTH = 280
NODE_HEADER_HEIGHT = 45
NODE_BORDER_RADIUS = 15
GRID_SIZE = 30