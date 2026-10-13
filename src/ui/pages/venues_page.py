"""
Venues Management Page for NiceGUI.
"""

from typing import List
from nicegui import ui

from core.models.venue import Venue
from ui.context import ServiceContainer
from ui.dialogs.venue_dialog import open_venue_dialog
from ui.layout import page_layout


def render_venues_page(container: ServiceContainer):
    """Renders the internship locations management view."""
    with page_layout(title="Locais de Estágio", active_path="/venues"):
        # Header and Actions
        with ui.row().classes("w-full justify-between items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0"):
                ui.label("Locais de Estágio").classes("text-2xl sm:text-3xl font-extrabold text-slate-900")
                ui.label("Instituições conveniadas, supervisores e capacidade de vagas.").classes("text-sm text-slate-500")

            ui.button(
                "Novo Local",
                icon="add_location_alt",
                on_click=lambda: open_venue_dialog(
                    venue_service=container.venue_service,
                    on_success=refresh_table,
                ),
            ).props("color=primary")

        # Filters Card
        with ui.card().classes("w-full p-4 card-shadow"):
            with ui.row().classes("items-center gap-4 flex-wrap"):
                occupancy_select = ui.select(
                    label="Filtrar por Ocupação",
                    options=["Todos", "Com Alunos Vinculados", "Sem Alunos Vinculados"],
                    value="Todos",
                ).classes("w-64").props("outlined dense")

                search_input = ui.input(
                    placeholder="Buscar por nome ou endereço...",
                ).classes("flex-1 min-w-48").props("outlined dense")
                with search_input.add_slot("prepend"):
                    ui.icon("search")

        # Table / Cards Container
        table_container = ui.column().classes("w-full gap-3")

        def refresh_table():
            table_container.clear()
            all_venues = container.venue_service.get_all()
            all_interns = container.intern_service.get_all_interns()

            # Group active interns by venue
            venue_interns_map = {}
            for i in all_interns:
                if i.is_active and i.venue_id:
                    venue_interns_map.setdefault(i.venue_id, []).append(i)

            occ_filter = occupancy_select.value
            query = (search_input.value or "").lower().strip()

            filtered: List[Venue] = []
            for v in all_venues:
                if query:
                    name_m = query in (v.venue_name or "").lower()
                    addr_m = query in (v.address or "").lower()
                    if not (name_m or addr_m):
                        continue

                allocated_count = len(venue_interns_map.get(v.venue_id, []))
                if occ_filter == "Com Alunos Vinculados" and allocated_count == 0:
                    continue
                if occ_filter == "Sem Alunos Vinculados" and allocated_count > 0:
                    continue

                filtered.append(v)

            with table_container:
                ui.label(f"Exibindo {len(filtered)} local(is)").classes("text-xs text-slate-500 px-1")

                if not filtered:
                    with ui.card().classes("w-full p-8 card-shadow items-center justify-center gap-2"):
                        ui.icon("location_off", size="xl").classes("text-slate-300")
                        ui.label("Nenhum local de estágio encontrado.").classes("text-slate-500")
                    return

                for venue in filtered:
                    allocated_interns = venue_interns_map.get(venue.venue_id, [])
                    allocated_count = len(allocated_interns)

                    with ui.card().classes("w-full p-4 card-shadow flex-col sm:flex-row items-start sm:items-center justify-between gap-3"):
                        # Venue Details
                        with ui.row().classes("items-center gap-3"):
                            ui.avatar("business", color="blue-1", text_color="primary", size="lg")
                            with ui.column().classes("gap-0"):
                                ui.label(venue.venue_name).classes("font-bold text-base text-slate-900")
                                if venue.address:
                                    ui.label(venue.address).classes("text-xs text-slate-500")

                                if venue.supervisor_name:
                                    ui.label(f"Supervisor: {venue.supervisor_name}").classes("text-xs text-slate-700 font-medium")

                        # Capacity / Interns
                        with ui.row().classes("items-center gap-6"):
                            with ui.column().classes("gap-0 items-start sm:items-center text-xs"):
                                ui.label("ALOCAÇÃO").classes("font-bold text-slate-400")
                                ui.badge(f"{allocated_count} aluno(s)", color="blue-7").classes("font-semibold text-xs")

                            # Actions
                            with ui.row().classes("items-center gap-1"):
                                # WhatsApp shortcut
                                if venue.supervisor_phone:
                                    formatted = container.communication_service.format_whatsapp_number(venue.supervisor_phone)
                                    if formatted:
                                        ui.button(
                                            icon="chat",
                                            on_click=lambda f=formatted: ui.navigate.to(f"https://wa.me/{f}", new_tab=True),
                                        ).props("flat round dense size=sm color=green-7").tooltip("Abrir WhatsApp")

                                # Email shortcut
                                if venue.supervisor_email:
                                    ui.button(
                                        icon="email",
                                        on_click=lambda em=venue.supervisor_email: ui.navigate.to(f"mailto:{em}", new_tab=True),
                                    ).props("flat round dense size=sm color=blue-7").tooltip("Enviar E-mail")

                                ui.button(
                                    icon="edit",
                                    on_click=lambda v=venue: open_venue_dialog(
                                        venue_service=container.venue_service,
                                        venue=v,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=primary").tooltip("Editar Local")

                                ui.button(
                                    icon="delete",
                                    on_click=lambda v=venue: confirm_delete_venue(v),
                                ).props("flat round dense size=sm color=negative").tooltip("Excluir Local")

        def confirm_delete_venue(venue: Venue):
            with ui.dialog() as del_dialog, ui.card().classes("p-6 dialog-card"):
                ui.label("Confirmar Exclusão").classes("text-lg font-bold text-slate-800")
                ui.label(f"Deseja excluir o local '{venue.name}'?").classes("text-sm text-slate-600")

                with ui.row().classes("w-full justify-end gap-2 pt-4"):
                    ui.button("Cancelar", on_click=del_dialog.close).props("flat color=grey")

                    def do_del():
                        if venue.venue_id:
                            container.venue_service.delete(venue.venue_id)
                            ui.notify("Local excluído.", color="info")
                            del_dialog.close()
                            refresh_table()

                    ui.button("Excluir", icon="delete", on_click=do_del).props("color=negative")
            del_dialog.open()

        occupancy_select.on("update:model-value", lambda _: refresh_table())
        search_input.on("update:model-value", lambda _: refresh_table())

        refresh_table()
