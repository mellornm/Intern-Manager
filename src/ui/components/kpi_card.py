"""
KPI Metric Card component for NiceGUI.
"""

from typing import Callable, Optional
from nicegui import ui


def create_kpi_card(
    title: str,
    value: str | int,
    icon: str,
    color_class: str = "text-blue-600",
    bg_color_class: str = "bg-blue-50",
    on_click: Optional[Callable] = None,
):
    """
    Renders an interactive KPI metric card with icon and value.
    """
    cursor_class = "cursor-pointer hover:shadow-md transition-shadow" if on_click else ""
    with ui.card().classes(f"p-5 w-full flex-row items-center justify-between card-shadow {cursor_class}") as card:
        if on_click:
            card.on("click", on_click)

        with ui.column().classes("gap-1"):
            ui.label(str(value)).classes("text-3xl font-extrabold text-slate-800 tracking-tight")
            ui.label(title.upper()).classes("text-xs font-semibold text-slate-500 tracking-wider")

        with ui.avatar(icon, size="lg").classes(f"{bg_color_class} {color_class}"):
            pass

    return card
