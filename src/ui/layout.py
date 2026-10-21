"""
Master layout for InternManager Pro Web.
Provides a modern, responsive Quasar shell with Header, Drawer, and Navigation
optimized for Desktop, Tablet, and Mobile viewports.
"""

from contextlib import contextmanager

from nicegui import ui

from ui.theme import apply_theme

NAV_ITEMS = [
    {"label": "Dashboard", "icon": "dashboard", "path": "/"},
    {"label": "Estagiários", "icon": "groups", "path": "/interns"},
    {"label": "Locais de Estágio", "icon": "location_on", "path": "/venues"},
    {"label": "Critérios de Notas", "icon": "rule", "path": "/criteria"},
    {"label": "Calendário", "icon": "calendar_month", "path": "/calendar"},
    {"label": "Configurações", "icon": "settings", "path": "/settings"},
]


@contextmanager
def page_layout(title: str, active_path: str = "/"):
    """
    Context manager providing consistent header, sidebar drawer, and main content area.
    Automatically collapses drawer into overlay on tablet/mobile (< 1024px).
    """
    apply_theme()

    with ui.header().classes(
        "bg-slate-900 text-white items-center justify-between px-3 sm:px-5 py-2.5 shadow-sm border-b border-slate-800"
    ):
        with ui.row().classes("items-center gap-2 no-wrap"):
            drawer_btn = ui.button(icon="menu").props("flat round dense color=white")
            with ui.row().classes("items-center gap-2 cursor-pointer").on(
                "click", lambda: ui.navigate.to("/")
            ):
                ui.avatar("school", color="blue-7", text_color="white", size="sm").classes(
                    "rounded-lg"
                )
                ui.label("InternManager").classes(
                    "text-base sm:text-lg font-extrabold tracking-tight text-white"
                )
                ui.badge("PRO", color="blue-8", text_color="blue-1").classes(
                    "text-[10px] font-bold px-1.5 py-0.5 rounded"
                )

        with ui.row().classes("items-center gap-2 sm:gap-3"):
            with ui.row().classes(
                "hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs text-slate-300"
            ):
                ui.icon("folder_special", size="14px").classes("text-blue-400")
                ui.label(title).classes("font-medium")

            ui.button(
                icon="help_outline",
                on_click=lambda: ui.navigate.to(
                    "https://mellornm.github.io/Intern-Manager/", new_tab=True
                ),
            ).props("flat round dense color=grey-4 size=sm").tooltip("Documentação e Ajuda")

    with ui.left_drawer(value=True).props("breakpoint=1024 width=250").classes(
        "bg-slate-900 text-slate-100 p-0 flex flex-col justify-between border-r border-slate-800"
    ) as drawer:
        drawer_btn.on_click(drawer.toggle)

        with ui.column().classes("w-full p-0 gap-1"):
            # Brand sub-header
            with ui.row().classes(
                "w-full px-4 py-3.5 items-center gap-3 border-b border-slate-800/80"
            ):
                ui.icon("verified_user", size="sm").classes("text-blue-400")
                with ui.column().classes("gap-0"):
                    ui.label("Coordenação de Estágios").classes(
                        "font-bold text-xs text-slate-100 tracking-wide uppercase"
                    )
                    ui.label("Painel Acadêmico v3.1").classes("text-[11px] text-slate-400")

            # Navigation list
            with ui.list().classes("w-full px-2.5 py-3 gap-1"):
                for item in NAV_ITEMS:
                    is_active = active_path == item["path"]
                    item_classes = (
                        "bg-blue-600 text-white font-semibold shadow-xs"
                        if is_active
                        else "text-slate-300 hover:bg-slate-800/80 hover:text-white font-medium"
                    )
                    icon_color = "text-white" if is_active else "text-slate-400"
                    with ui.item(
                        on_click=lambda p=item["path"]: ui.navigate.to(p)
                    ).props("clickable v-ripple").classes(
                        f"w-full rounded-xl px-3 py-2.5 transition-colors {item_classes}"
                    ):
                        with ui.item_section().props("avatar").classes("min-w-0 pr-3"):
                            ui.icon(item["icon"], size="20px").classes(icon_color)
                        with ui.item_section():
                            ui.item_label(item["label"]).classes("text-sm")

        # Bottom drawer footer
        with ui.row().classes(
            "w-full px-4 py-3 border-t border-slate-800/80 text-[11px] text-slate-400 justify-between items-center"
        ):
            ui.label("InternManager Pro © 2026")
            with ui.row().classes("items-center gap-1 text-emerald-400"):
                ui.icon("lock", size="12px")
                ui.label("WAL Ativo").classes("text-[10px] font-semibold")

    # Main content container (responsive padding for mobile/tablet/desktop)
    with ui.column().classes(
        "w-full min-h-screen p-3 sm:p-5 lg:p-7 bg-slate-50 gap-4 sm:gap-5 max-w-[1600px] mx-auto"
    ):
        yield
