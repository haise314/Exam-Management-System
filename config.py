# Theme configuration for the entire application
THEME = {
    "colors": {
        "primary": "#2d5a9e",
        "primary_hover": "#1f4172",
        "secondary": "#6c757d",
        "background": "#f5f5f5",
        "surface": "#ffffff",
        "text": "#1a1a1a",
        "text_secondary": "#666666"
    },
    "fonts": {
        "heading": ("Helvetica", 24, "bold"),
        "subheading": ("Helvetica", 16, "bold"),
        "body": ("Helvetica", 12),
    },
    "padding": {
        "small": 5,
        "medium": 10,
        "large": 20
    }
}

# Button colors (moved from admin_dashboard.py)
BUTTON_COLORS = {
    "primary": (THEME["colors"]["primary"], THEME["colors"]["primary_hover"]),
    "secondary": ("#6c757d", "#495057"),
    "danger": ("#dc3545", "#c82333"),
    "success": ("#28a745", "#218838")
} 