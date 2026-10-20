"""
Master layout for InternManager Pro Web.
Provides a modern, responsive Quasar shell with Header, Drawer, and Navigation.
"""

from contextlib import contextmanager

from nicegui import ui

from ui.theme import apply_theme

NAV_ITEMS = [
    {"label": "Dashboard", "icon": "dashboard", "path": "/"},
    {"label": "Estagiários", "icon": "groups", "path": "/interns"},
    {"label": "Locais", "icon": "location_on", "path": "/venues"},
    {"label": "Critérios", "icon": "rule", "path": "/criteria"},
    {"label": "Calendário", "icon": "calendar_month", "path": "/calendar"},
    {"label": "Configurações", "icon": "settings", "path": "/settings"},
]


@contextmanager
def page_layout(title: str, active_path: str = "/"):
    """
    Context manager providing consistent header, sidebar drawer, and main content area.
    """
    apply_theme()

    with ui.header().classes(
        "bg-blue-900 text-white items-center justify-between px-4 py-2 shadow-md"
    ):
        with ui.row().classes("items-center gap-2"):
            drawer_btn = ui.button(icon="menu").props("flat round color=white")
            ui.icon("school", size="sm").classes("text-white")
            ui.label("InternManager Pro").classes("text-lg font-bold tracking-wide")
            ui.badge("v3.0", color="blue-7").classes("ml-2 text-xs")

        with ui.row().classes("items-center gap-4"):
            ui.label(title).classes("text-sm text-blue-200 hidden sm:inline")
            ui.button(
                icon="open_in_new",
                on_click=lambda: ui.navigate.to(
                    "https://mellornm.github.io/Intern-Manager/", new_tab=True
                ),
            ).props("flat round color=white size=sm").tooltip("Documentação")

    with ui.left_drawer(value=True).classes(
        "bg-slate-900 text-slate-100 p-0 flex flex-col justify-between"
    ) as drawer:
        drawer_btn.on_click(drawer.toggle)

        with ui.column().classes("w-full p-0 gap-1"):
            # Brand sub-header
            with ui.row().classes(
                "w-full p-4 items-center gap-3 border-b border-slate-800"
            ):
                ui.avatar("school", color="primary", text_color="white", size="md")
                with ui.column().classes("gap-0"):
                    ui.label("Supervisão de Estágios").classes(
                        "font-semibold text-sm text-white"
                    )
                    ui.label("Painel de Controle").classes("text-xs text-slate-400")

            # Navigation list
            with ui.list().classes("w-full px-2 py-3 gap-1"):
                for item in NAV_ITEMS:
                    is_active = active_path == item["path"]
                    bg_class = (
                        "bg-blue-800 text-white font-medium"
                        if is_active
                        else "text-slate-300 hover:bg-slate-800 hover:text-white"
                    )
                    with ui.item(
                        on_click=lambda p=item["path"]: ui.navigate.to(p)
                    ).classes(f"w-full rounded-lg cursor-pointer px-3 py-2 {bg_class}"):
                        with ui.item_section().props("avatar"):
                            ui.icon(item["icon"], size="sm")
                        with ui.item_section():
                            ui.item_label(item["label"]).classes("text-sm")

        # Bottom drawer footer
        with ui.row().classes(
            "w-full p-3 border-t border-slate-800 text-xs text-slate-400 justify-between items-center"
        ):
            ui.label("InternManager Pro © 2026")
            ui.icon("lock", size="xs").tooltip("Sessão Web Segura")

    # Main content container
    with ui.column().classes("w-full min-h-screen p-4 sm:p-6 lg:p-8 bg-slate-50 gap-6"):
        yield
