"""
Theme and styling definitions for the NiceGUI web interface.
Preserves the brand identity and color palette of InternManager Pro.
"""

COLORS = {
    "primary": "#005A9E",
    "primary_hover": "#004C87",
    "secondary": "#6C757D",
    "success": "#107C10",
    "warning": "#FFC107",
    "danger": "#D13438",
    "dark": "#323130",
    "medium": "#605E5C",
    "light": "#F8F9FA",
    "white": "#FFFFFF",
    "border": "#E1DFDD",
    "sidebar_bg": "#1F2937",
    "sidebar_text": "#F9FAFB",
}

# Common CSS snippets for nice presentation
GLOBAL_CSS = f"""
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: {COLORS['light']};
        color: {COLORS['dark']};
    }}
    .nicegui-content {{
        padding: 0 !important;
    }}
    .card-shadow {{
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background-color: #FFFFFF;
    }}
    .dialog-card {{
        border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }}
    .table-custom tr:hover {{
        background-color: #F1F5F9 !important;
    }}
"""


def apply_theme():
    """Applies global CSS styles to the current NiceGUI page."""
    from nicegui import ui
    ui.add_head_html(f"<style>{GLOBAL_CSS}</style>")
