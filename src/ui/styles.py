COLORS = {
    "primary": "#005A9E",
    "primary_hover": "#004C87",
    "secondary": "#6C757D",
    "success": "#107C10",
    "warning": "#FFC107",
    "danger": "#D13438",
    "dark": "#323130",
    "medium": "#605E5C",
    "light": "#F3F2F1",
    "white": "#FFFFFF",
    "border": "#E1DFDD",
    "sidebar_bg": "#201F1E",
    "sidebar_text": "#F3F2F1",
}


def get_color(key):
    return COLORS.get(key, "#000000")
