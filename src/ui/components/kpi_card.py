"""
KPI Metric Card component for NiceGUI.
Uses pure Tailwind icon containers to avoid Quasar q-avatar bg-primary conflicts.
"""

from typing import Callable, Optional
from nicegui import ui


def create_kpi_card(
    title: str,
    value: str | int,
    icon: str,
    color_class: str = "text-blue-600",
    bg_color_class: str = "bg-blue-50",
    border_color_class: str = "border-l-blue-600",
    icon_border_class: str = "border-blue-100",
    subtitle: Optional[str] = None,
    on_click: Optional[Callable] = None,
):
    """
    Renders an interactive, responsive KPI metric card with accent border and harmonious icon box.
    """
    cursor_class = (
        "cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all"
        if on_click
        else ""
    )
    with ui.card().classes(
        f"p-4 sm:p-5 w-full flex-row items-center justify-between bg-white rounded-xl border border-slate-200/80 border-l-4 {border_color_class} shadow-xs {cursor_class}"
    ) as card:
        if on_click:
            card.on("click", on_click)

        with ui.column().classes("gap-0.5 min-w-0 flex-1 pr-2"):
            ui.label(title.upper()).classes(
                "text-[11px] font-bold text-slate-500 tracking-wider truncate"
            )
            ui.label(str(value)).classes(
                "text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight"
            )
            if subtitle:
                ui.label(subtitle).classes(
                    "text-[11px] text-slate-400 font-medium truncate"
                )

        with ui.element("div").classes(
            f"w-12 h-12 rounded-xl flex items-center justify-center border {bg_color_class} {color_class} {icon_border_class} shrink-0"
        ):
            ui.icon(icon, size="24px")

    return card
