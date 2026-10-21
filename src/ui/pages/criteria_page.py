"""
Evaluation Criteria Management Page for NiceGUI.
Refactored for responsive PC, Tablet, and Mobile layouts.
"""

from nicegui import ui

from core.models.evaluation_criteria import EvaluationCriteria
from ui.context import ServiceContainer
from ui.dialogs.criteria_dialog import open_criteria_dialog
from ui.layout import page_layout


def render_criteria_page(container: ServiceContainer):
    """Renders the grading criteria list and management view."""
    with page_layout(title="Critérios de Avaliação", active_path="/criteria"):
        # Header and Actions
        with ui.row().classes("w-full justify-between items-start sm:items-center gap-3 flex-wrap"):
            with ui.column().classes("gap-0.5"):
                ui.label("Critérios de Avaliação").classes(
                    "text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight"
                )
                ui.label(
                    "Parâmetros e pesos máximos utilizados para o cálculo de avaliação dos estagiários."
                ).classes("text-xs sm:text-sm text-slate-500")

            ui.button(
                "Novo Critério",
                icon="add",
                on_click=lambda: open_criteria_dialog(
                    service=container.criteria_service,
                    on_success=refresh_table,
                ),
            ).props("unelevated no-caps color=primary").classes(
                "px-4 font-semibold shadow-xs w-full sm:w-auto"
            )

        table_container = ui.column().classes("w-full gap-2.5")

        def refresh_table():
            table_container.clear()
            criteria_list = container.criteria_service.list_active_criteria()

            with table_container:
                if not criteria_list:
                    with ui.card().classes(
                        "w-full py-12 bg-white border border-slate-200/80 rounded-xl items-center justify-center gap-2 shadow-none"
                    ):
                        ui.icon("rule", size="xl").classes("text-slate-300")
                        ui.label("Nenhum critério de avaliação cadastrado.").classes(
                            "text-slate-600 font-semibold text-sm"
                        )
                    return

                total_weight = sum(c.weight for c in criteria_list if c.weight)
                with ui.row().classes(
                    "w-full px-4 py-2 bg-slate-100/80 border border-slate-200/70 rounded-lg items-center justify-between text-xs font-semibold text-slate-500 uppercase tracking-wider"
                ):
                    ui.label(f"Critérios Ativos ({len(criteria_list)})")
                    ui.badge(
                        f"Soma dos Pesos: {total_weight:.1f} pts",
                        color="blue-1",
                        text_color="blue-9",
                    ).classes("text-xs font-bold px-2.5 py-0.5 rounded")

                for crit in criteria_list:
                    with ui.card().classes(
                        "w-full px-4 py-3.5 rounded-xl border border-slate-200/80 bg-white shadow-xs hover:shadow-sm transition-all flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
                    ):
                        with ui.row().classes("items-start sm:items-center gap-3 min-w-0 flex-1"):
                            ui.avatar(
                                "rule",
                                color="blue-1",
                                text_color="blue-9",
                                size="md",
                            ).classes("rounded-xl shrink-0")
                            with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                                ui.label(crit.name).classes(
                                    "font-bold text-sm sm:text-base text-slate-900 truncate"
                                )
                                ui.label(
                                    crit.description or "Sem descrição complementar cadastrada."
                                ).classes("text-xs text-slate-500")

                        with ui.row().classes(
                            "items-center justify-between sm:justify-end gap-3 w-full sm:w-auto pt-2 sm:pt-0 border-t border-slate-100 sm:border-0"
                        ):
                            ui.badge(
                                f"Peso Máx: {crit.weight:.1f}",
                                color="blue-1",
                                text_color="blue-9",
                            ).classes("text-xs font-bold px-3 py-1 rounded-md border border-blue-200")

                            with ui.row().classes("items-center gap-1"):
                                ui.button(
                                    icon="edit",
                                    on_click=lambda c=crit: open_criteria_dialog(
                                        service=container.criteria_service,
                                        criteria=c,
                                        on_success=refresh_table,
                                    ),
                                ).props("flat round dense size=sm color=slate-600").tooltip(
                                    "Editar Critério"
                                )

                                ui.button(
                                    icon="delete_outline",
                                    on_click=lambda c=crit: confirm_delete_criteria(c),
                                ).props("flat round dense size=sm color=negative").tooltip(
                                    "Excluir Critério"
                                )

        def confirm_delete_criteria(crit: EvaluationCriteria):
            with ui.dialog() as del_dialog, ui.card().classes(
                "p-5 sm:p-6 rounded-2xl max-w-md w-full"
            ):
                with ui.row().classes("items-center gap-3 pb-2"):
                    ui.avatar("warning_amber", color="red-1", text_color="red-7", size="md")
                    with ui.column().classes("gap-0"):
                        ui.label("Confirmar Exclusão").classes("text-base font-bold text-slate-900")
                        ui.label("Critérios com notas vinculadas não podem ser removidos.").classes(
                            "text-xs text-slate-500"
                        )

                ui.label(f"Deseja excluir o critério '{crit.name}'?").classes(
                    "text-sm text-slate-700 py-2"
                )

                with ui.row().classes("w-full justify-end gap-2 pt-3 border-t border-slate-100"):
                    ui.button("Cancelar", on_click=del_dialog.close).props(
                        "flat no-caps color=grey-7"
                    )

                    def do_del():
                        if crit.criteria_id:
                            try:
                                container.criteria_service.delete_criteria(crit)
                                ui.notify("Critério excluído.", color="info")
                                del_dialog.close()
                                refresh_table()
                            except Exception as e:
                                ui.notify(f"Não foi possível excluir: {e}", color="negative")

                    ui.button("Excluir Critério", icon="delete", on_click=do_del).props(
                        "unelevated no-caps color=negative"
                    )
            del_dialog.open()

        refresh_table()
