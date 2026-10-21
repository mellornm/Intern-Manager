"""
Venues Management Page for NiceGUI.
Refactored with a 12-column responsive tabular layout for PC, Tablet, and Mobile.
"""

from typing import List
from nicegui import ui

from core.models.venue import Venue
from ui.context import ServiceContainer
from ui.dialogs.quick_view_dialogs import open_venue_quick_view
from ui.dialogs.venue_dialog import open_venue_dialog
from ui.layout import page_layout


def render_venues_page(container: ServiceContainer):
    """Renders the internship locations management view."""
    with page_layout(title="Locais de Estágio", active_path="/venues"):
        # Header and Actions
        with ui.row().classes("w-full justify-between items-start sm:items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0.5"):
                ui.label("Locais de Estágio").classes(
                    "text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Instituições conveniadas, preceptores de campo e alunos alocados."
                ).classes("text-xs sm:text-sm text-slate-500")

            ui.button(
                "Novo Local de Estágio",
                icon="add_location_alt",
                on_click=lambda: open_venue_dialog(
                    venue_service=container.venue_service,
                    on_success=refresh_table,
                ),
            ).props("unelevated no-caps color=primary").classes(
                "px-4 font-semibold shadow-xs w-full sm:w-auto"
            )

        # Filters Toolbar
        with ui.card().classes(
            "w-full p-3 sm:p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-xs"
        ):
            with ui.element("div").classes(
                "w-full grid grid-cols-1 sm:grid-cols-12 items-center gap-3"
            ):
                search_input = (
                    ui.input(
                        placeholder="Buscar por nome da instituição, preceptor ou endereço...",
                    )
                    .classes("sm:col-span-8 w-full")
                    .props("outlined dense clearable debounce=250 hide-bottom-space")
                )
                with search_input.add_slot("prepend"):
                    ui.icon("search", size="xs").classes("text-slate-400")

                occupancy_select = (
                    ui.select(
                        label="Ocupação",
                        options=["Todos", "Com Alunos Vinculados", "Sem Alunos Vinculados"],
                        value="Todos",
                    )
                    .classes("sm:col-span-4 w-full")
                    .props("outlined dense options-dense hide-bottom-space")
                )

        # Table / Cards Container
        table_container = ui.column().classes("w-full gap-2.5")

        def refresh_table():
            table_container.clear()
            all_venues = container.venue_service.get_all()
            all_interns = container.intern_service.get_all_interns()

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
                    sup_m = query in (v.supervisor_name or "").lower()
                    if not (name_m or addr_m or sup_m):
                        continue

                allocated_count = len(venue_interns_map.get(v.venue_id, []))
                if occ_filter == "Com Alunos Vinculados" and allocated_count == 0:
                    continue
                if occ_filter == "Sem Alunos Vinculados" and allocated_count > 0:
                    continue

                filtered.append(v)

            with table_container:
                # Desktop Column Header
                with ui.row().classes(
                    "w-full px-4 py-2 bg-slate-100/80 border border-slate-200/70 rounded-lg items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider"
                ):
                    ui.label(f"Instituições Conveniadas ({len(filtered)})")
                    with ui.row().classes("hidden lg:flex items-center gap-16 pr-6"):
                        ui.label("Preceptor / Contato").classes("w-52")
                        ui.label("Estagiários Ativos").classes("w-32 text-center")
                        ui.label("Ações").classes("w-28 text-right")

                if not filtered:
                    with ui.card().classes(
                        "w-full py-12 bg-white border border-slate-200/80 rounded-xl items-center justify-center gap-2 shadow-none"
                    ):
                        ui.icon("location_off", size="xl").classes("text-slate-300")
                        ui.label("Nenhum local de estágio encontrado.").classes(
                            "text-slate-600 font-semibold text-sm"
                        )
                    return

                for venue in filtered:
                    allocated_interns = venue_interns_map.get(venue.venue_id, [])
                    allocated_count = len(allocated_interns)

                    with ui.card().classes(
                        "w-full px-3.5 sm:px-4 py-3.5 rounded-xl border border-slate-200/80 bg-white shadow-xs hover:shadow-sm hover:border-slate-300 transition-all"
                    ):
                        with ui.element("div").classes(
                            "w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 items-center gap-3 lg:gap-4"
                        ):
                            # COL 1-5: Institution & Address
                            with ui.row().classes(
                                "sm:col-span-2 lg:col-span-5 items-start sm:items-center gap-3 no-wrap min-w-0"
                            ):
                                ui.avatar(
                                    "domain",
                                    color="blue-1",
                                    text_color="blue-9",
                                    size="md",
                                ).classes("rounded-xl shrink-0 cursor-pointer").on(
                                    "click",
                                    lambda v=venue: open_venue_quick_view(
                                        v, container, on_change=refresh_table
                                    ),
                                )

                                with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                                    ui.label(venue.venue_name).classes(
                                        "font-bold text-sm text-slate-900 hover:text-blue-700 cursor-pointer truncate transition-colors"
                                    ).on(
                                        "click",
                                        lambda v=venue: open_venue_quick_view(
                                            v, container, on_change=refresh_table
                                        ),
                                    ).tooltip("Clique para ver os estagiários alocados neste local")
                                    with ui.row().classes("items-center gap-1 text-xs text-slate-500 min-w-0"):
                                        ui.icon("place", size="14px").classes("text-slate-400 shrink-0")
                                        ui.label(
                                            venue.address or "Endereço não cadastrado"
                                        ).classes("truncate")

                            # COL 6-8: Supervisor & Contact Info
                            with ui.column().classes("sm:col-span-1 lg:col-span-3 gap-0.5 min-w-0"):
                                ui.label("PRECEPTOR LOCAL").classes(
                                    "lg:hidden text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                with ui.row().classes("items-center gap-1.5 text-xs font-semibold text-slate-800"):
                                    ui.icon("person_pin", size="15px").classes("text-blue-600 shrink-0")
                                    ui.label(venue.supervisor_name or "Não informado").classes("truncate")

                                with ui.row().classes("items-center gap-3 text-[11px] text-slate-500 flex-wrap"):
                                    if venue.supervisor_phone:
                                        ui.label(f"Tel: {venue.supervisor_phone}")
                                    if venue.supervisor_email:
                                        ui.label(venue.supervisor_email).classes("truncate max-w-44")

                            # COL 9-10: Allocated Interns Badge (Clickable)
                            with ui.column().classes(
                                "sm:col-span-1 lg:col-span-2 items-start lg:items-center gap-1 cursor-pointer"
                            ).on(
                                "click",
                                lambda v=venue: open_venue_quick_view(
                                    v, container, on_change=refresh_table
                                ),
                            ):
                                ui.label("OCUPAÇÃO").classes(
                                    "lg:hidden text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                badge_color = "blue-1" if allocated_count > 0 else "grey-2"
                                badge_txt = "blue-9" if allocated_count > 0 else "grey-7"
                                ui.badge(
                                    f"{allocated_count} estagiário(s)",
                                    color=badge_color,
                                    text_color=badge_txt,
                                ).classes(
                                    "font-bold text-xs px-2.5 py-1 rounded-md border border-slate-200/80 hover:border-blue-400 transition-colors"
                                )

                            # COL 11-12: Quick Contact & Edit/Delete Actions
                            with ui.row().classes(
                                "sm:col-span-2 lg:col-span-2 items-center justify-end gap-1 pt-2 lg:pt-0 border-t border-slate-100 lg:border-0 w-full"
                            ):
                                ui.button(
                                    icon="visibility",
                                    on_click=lambda v=venue: open_venue_quick_view(
                                        v, container, on_change=refresh_table
                                    ),
                                ).props("flat round dense size=sm color=blue-8").tooltip(
                                    "Ver Alunos Vinculados e Detalhes do Local"
                                )
                                if venue.supervisor_phone:
                                    formatted = container.communication_service.format_whatsapp_number(
                                        venue.supervisor_phone
                                    )
                                    if formatted:
                                        ui.button(
                                            icon="chat",
                                            on_click=lambda f=formatted: ui.navigate.to(
                                                f"https://wa.me/{f}", new_tab=True
                                            ),
                                        ).props("flat round dense size=sm color=green-7").tooltip(
                                            "Conversar no WhatsApp"
                                        )

                                if venue.supervisor_email:
                                    ui.button(
                                        icon="mail_outline",
                                        on_click=lambda em=venue.supervisor_email: ui.navigate.to(
                                            f"mailto:{em}", new_tab=True
                                        ),
                                    ).props("flat round dense size=sm color=blue-7").tooltip(
                                        "Enviar E-mail ao Preceptor"
                                    )

                                ui.button(
                                    icon="edit",
                                    on_click=lambda v=venue: open_venue_dialog(
                                        venue_service=container.venue_service,
                                        venue=v,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=slate-600").tooltip(
                                    "Editar Local"
                                )

                                ui.button(
                                    icon="delete_outline",
                                    on_click=lambda v=venue: confirm_delete_venue(v),
                                ).props("flat round dense size=sm color=negative").tooltip(
                                    "Excluir Local"
                                )

        def confirm_delete_venue(venue: Venue):
            with ui.dialog() as del_dialog, ui.card().classes(
                "p-5 sm:p-6 rounded-2xl max-w-md w-full"
            ):
                with ui.row().classes("items-center gap-3 pb-2"):
                    ui.avatar("warning_amber", color="red-1", text_color="red-7", size="md")
                    with ui.column().classes("gap-0"):
                        ui.label("Confirmar Exclusão").classes("text-base font-bold text-slate-900")
                        ui.label("A instituição será removida da listagem.").classes(
                            "text-xs text-slate-500"
                        )

                ui.label(
                    f"Deseja realmente excluir o local '{venue.venue_name}'?"
                ).classes("text-sm text-slate-700 py-2")

                with ui.row().classes("w-full justify-end gap-2 pt-3 border-t border-slate-100"):
                    ui.button("Cancelar", on_click=del_dialog.close).props(
                        "flat no-caps color=grey-7"
                    )

                    def do_del():
                        if venue.venue_id:
                            container.venue_service.delete_venue(venue)
                            ui.notify("Local excluído.", color="info")
                            del_dialog.close()
                            refresh_table()

                    ui.button("Excluir Local", icon="delete", on_click=do_del).props(
                        "unelevated no-caps color=negative"
                    )
            del_dialog.open()

        occupancy_select.on_value_change(lambda _: refresh_table())
        search_input.on_value_change(lambda _: refresh_table())

        refresh_table()
