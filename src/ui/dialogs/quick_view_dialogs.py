"""
Quick View (360° Dossier) Dialogs for Interns and Venues.
Provides instant 1-click access to essential metrics, contacts, attendance,
grades, pending documents, incidents/attachments, and allocated interns.
"""

from typing import Callable, Optional
from nicegui import ui

from config import USER_DATA_ROOT
from core.models.intern import Intern
from core.models.venue import Venue
from ui.components.status_badge import create_status_badge
from ui.context import ServiceContainer
from ui.dialogs.document_dialog import open_document_dialog
from ui.dialogs.grade_dialog import open_grade_dialog
from ui.dialogs.intern_dialog import open_intern_dialog
from ui.dialogs.meeting_dialog import open_meeting_dialog
from ui.dialogs.observation_dialog import open_observation_dialog
from ui.dialogs.report_dialog import open_report_dialog
from ui.dialogs.venue_dialog import open_venue_dialog
from ui.dialogs.visit_dialog import open_visit_dialog


def _get_initials(name: str) -> str:
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return "AL"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[-1][0]}".upper()


def open_intern_quick_view(
    intern: Intern,
    container: ServiceContainer,
    on_change: Optional[Callable] = None,
):
    """Opens the 360° Quick View Dossier for an intern."""
    if not intern.intern_id:
        return

    attachments_dir = USER_DATA_ROOT / "attachments"

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-3xl p-0 rounded-2xl overflow-hidden shadow-2xl border border-slate-200"
    ):
        content_box = ui.column().classes("w-full gap-0")

        def notify_and_refresh():
            render_dossier()
            if on_change:
                on_change()

        def render_dossier():
            content_box.clear()
            fresh_intern = (
                container.intern_service.get_by_id(intern.intern_id)
                if intern.intern_id
                else intern
            ) or intern

            i_id = fresh_intern.intern_id or 0
            venue = (
                container.venue_service.get_by_id(fresh_intern.venue_id)
                if fresh_intern.venue_id
                else None
            )
            docs = container.document_service.get_by_intern_id(i_id)
            meetings = container.meeting_service.get_by_intern_id(i_id)
            grades = container.grade_service.get_by_intern_id(i_id)
            criteria_list = container.criteria_service.list_active_criteria()
            observations = container.observation_service.get_by_intern_id(i_id)
            visits = container.visit_service.get_by_intern_id(i_id)

            # Metrics calculation
            total_meetings = len(meetings)
            present_meetings = sum(1 for m in meetings if m.is_intern_present)
            freq_pct = (
                int((present_meetings / total_meetings) * 100)
                if total_meetings > 0
                else 0
            )

            grades_map = {
                g.criteria_id: g.value for g in grades if g.criteria_id is not None
            }
            total_score = sum(
                grades_map.get(c.criteria_id, 0.0)
                for c in criteria_list
                if c.criteria_id
            )
            max_weight = sum(c.weight for c in criteria_list if c.weight)

            total_docs = len(docs)
            approved_docs = sum(
                1 for d in docs if (d.status or "").lower() == "aprovado"
            )
            pending_docs = [
                d for d in docs if (d.status or "").lower() != "aprovado"
            ]

            incident_count = sum(
                1 for o in observations if getattr(o, "is_incident", False)
            )

            with content_box:
                # 1. Header Banner with Instant Contact Actions
                with ui.row().classes(
                    "w-full px-5 sm:px-6 py-4 bg-slate-900 text-white items-start sm:items-center justify-between gap-3"
                ):
                    with ui.row().classes("items-center gap-3 min-w-0 flex-1"):
                        ui.avatar(
                            _get_initials(fresh_intern.name),
                            color="blue-7",
                            text_color="white",
                            size="lg",
                        ).classes("font-extrabold text-sm rounded-xl shrink-0")

                        with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                            with ui.row().classes("items-center gap-2 flex-wrap"):
                                ui.label(fresh_intern.name).classes(
                                    "text-base sm:text-lg font-extrabold text-white truncate"
                                )
                                create_status_badge(fresh_intern.status)
                                if incident_count > 0:
                                    ui.badge(
                                        f"⚠️ {incident_count} Ocorrência(s)",
                                        color="red-6",
                                        text_color="white",
                                    ).classes("text-[10px] font-bold px-2 py-0.5 rounded")

                            with ui.row().classes(
                                "items-center gap-3 text-xs text-slate-300 flex-wrap"
                            ):
                                ui.label(
                                    f"RA: {fresh_intern.registration_number or 'S/N'}"
                                ).classes("font-mono")
                                ui.label(f"• Semestre: {fresh_intern.term or 'N/I'}")
                                if fresh_intern.phone:
                                    ui.label(f"• Tel: {fresh_intern.phone}")

                    with ui.row().classes("items-center gap-1.5 shrink-0"):
                        if fresh_intern.phone:
                            wa_num = container.communication_service.format_whatsapp_number(
                                fresh_intern.phone
                            )
                            if wa_num:
                                ui.button(
                                    icon="chat",
                                    on_click=lambda n=wa_num: ui.navigate.to(
                                        f"https://wa.me/{n}", new_tab=True
                                    ),
                                ).props(
                                    "unelevated round dense size=sm color=green-6"
                                ).tooltip("WhatsApp do Aluno")

                        if fresh_intern.email:
                            ui.button(
                                icon="mail_outline",
                                on_click=lambda em=fresh_intern.email: ui.navigate.to(
                                    f"mailto:{em}", new_tab=True
                                ),
                            ).props(
                                "unelevated round dense size=sm color=blue-7"
                            ).tooltip(f"E-mail: {fresh_intern.email}")

                        ui.button(
                            icon="edit",
                            on_click=lambda: open_intern_dialog(
                                intern_service=container.intern_service,
                                venue_service=container.venue_service,
                                intern=fresh_intern,
                                on_success=notify_and_refresh,
                            ),
                        ).props(
                            "flat round dense size=sm color=white"
                        ).tooltip("Editar Cadastro")

                        ui.button(icon="close", on_click=dialog.close).props(
                            "flat round dense size=sm color=grey-4"
                        )

                # 2. Scrollable Body
                with ui.column().classes(
                    "w-full px-5 sm:px-6 py-4 gap-4 max-h-[75vh] overflow-y-auto bg-slate-50"
                ):
                    # 4 Interactive Mini-KPI Cards
                    with ui.grid(columns=1).classes(
                        "w-full sm:grid-cols-2 lg:grid-cols-4 gap-3"
                    ):
                        # Card 1: Meetings Attendance
                        with ui.card().classes(
                            "p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-none cursor-pointer hover:border-blue-400 transition-all gap-1 min-w-0"
                        ).on(
                            "click",
                            lambda: open_meeting_dialog(
                                intern=fresh_intern,
                                service=container.meeting_service,
                                on_close=notify_and_refresh,
                            ),
                        ):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("REUNIÕES").classes(
                                    "text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                ui.icon("event_available", size="16px").classes(
                                    "text-blue-600"
                                )
                            ui.label(
                                f"{present_meetings}/{total_meetings} presenças"
                            ).classes("text-base font-extrabold text-slate-900")
                            ui.label(
                                f"Frequência: {freq_pct}%"
                                if total_meetings
                                else "Nenhuma registrada"
                            ).classes("text-[11px] text-slate-500 font-medium")

                        # Card 2: Grades / Score
                        with ui.card().classes(
                            "p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-none cursor-pointer hover:border-amber-400 transition-all gap-1 min-w-0"
                        ).on(
                            "click",
                            lambda: open_grade_dialog(
                                intern=fresh_intern,
                                criteria_service=container.criteria_service,
                                grade_service=container.grade_service,
                                on_success=notify_and_refresh,
                            ),
                        ):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("DESEMPENHO").classes(
                                    "text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                ui.icon("grade", size="16px").classes("text-amber-600")
                            ui.label(
                                f"{total_score:.1f} / {max_weight:.1f} pts"
                            ).classes("text-base font-extrabold text-slate-900")
                            ui.label(
                                f"{len(grades)}/{len(criteria_list)} critérios avaliados"
                            ).classes("text-[11px] text-slate-500 font-medium")

                        # Card 3: Documents
                        with ui.card().classes(
                            "p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-none cursor-pointer hover:border-emerald-400 transition-all gap-1 min-w-0"
                        ).on(
                            "click",
                            lambda: open_document_dialog(
                                intern=fresh_intern,
                                service=container.document_service,
                                on_close=notify_and_refresh,
                            ),
                        ):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("DOCUMENTOS").classes(
                                    "text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                ui.icon("folder_open", size="16px").classes(
                                    "text-emerald-600"
                                )
                            ui.label(
                                f"{approved_docs}/{total_docs} aprovados"
                            ).classes("text-base font-extrabold text-slate-900")
                            ui.label(
                                "100% em dia"
                                if not pending_docs and total_docs > 0
                                else f"{len(pending_docs)} pendente(s)"
                            ).classes(
                                "text-[11px] font-medium "
                                + (
                                    "text-emerald-600"
                                    if not pending_docs and total_docs > 0
                                    else "text-amber-700"
                                )
                            )

                        # Card 4: Observations & Incidents
                        inc_border = (
                            "border-rose-300 bg-rose-50/40"
                            if incident_count > 0
                            else "border-slate-200/80 bg-white"
                        )
                        with ui.card().classes(
                            f"p-3.5 border {inc_border} rounded-xl shadow-none cursor-pointer hover:border-rose-400 transition-all gap-1 min-w-0"
                        ).on(
                            "click",
                            lambda: open_observation_dialog(
                                intern=fresh_intern,
                                service=container.observation_service,
                                on_close=notify_and_refresh,
                            ),
                        ):
                            with ui.row().classes("w-full justify-between items-center"):
                                ui.label("OCORRÊNCIAS / OBS.").classes(
                                    "text-[10px] font-bold text-slate-400 tracking-wider"
                                )
                                ui.icon(
                                    "warning_amber" if incident_count else "notes",
                                    size="16px",
                                ).classes(
                                    "text-rose-600"
                                    if incident_count
                                    else "text-slate-500"
                                )
                            ui.label(f"{len(observations)} registro(s)").classes(
                                "text-base font-extrabold text-slate-900"
                            )
                            ui.label(
                                f"⚠️ {incident_count} ocorrência(s)"
                                if incident_count
                                else "Sem intercorrências"
                            ).classes(
                                "text-[11px] font-semibold "
                                + (
                                    "text-rose-700"
                                    if incident_count
                                    else "text-slate-500"
                                )
                            )

                    # 3. Field Allocation & Schedule Details (2 Pure Cards)
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-3"):
                        # Left: Venue & Preceptor
                        with ui.card().classes(
                            "p-4 bg-white border border-slate-200/80 rounded-xl shadow-none gap-2 min-w-0"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center pb-1.5 border-b border-slate-100"
                            ):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("domain", size="16px").classes(
                                        "text-blue-700"
                                    )
                                    ui.label("CAMPO DE ESTÁGIO & PRECEPTOR").classes(
                                        "text-xs font-bold text-slate-700 tracking-wider"
                                    )
                                ui.button(
                                    f"Visitas ({len(visits)})",
                                    icon="pin_drop",
                                    on_click=lambda: open_visit_dialog(
                                        intern=fresh_intern,
                                        service=container.visit_service,
                                        venue_service=container.venue_service,
                                        on_close=notify_and_refresh,
                                    ),
                                ).props(
                                    "flat dense no-caps size=xs color=primary"
                                ).classes("font-semibold")

                            if venue:
                                ui.label(venue.venue_name).classes(
                                    "font-bold text-sm text-slate-900 break-words w-full"
                                )
                                ui.label(
                                    venue.address or "Endereço não cadastrado"
                                ).classes("text-xs text-slate-500 break-words w-full")
                                with ui.row().classes(
                                    "w-full items-center justify-between pt-2 border-t border-slate-100 mt-1"
                                ):
                                    with ui.column().classes("gap-0 min-w-0 flex-1"):
                                        ui.label(
                                            f"Preceptor: {venue.supervisor_name or 'Não informado'}"
                                        ).classes(
                                            "text-xs font-semibold text-slate-800 break-words"
                                        )
                                        if venue.supervisor_phone:
                                            ui.label(
                                                f"Tel: {venue.supervisor_phone}"
                                            ).classes("text-[11px] text-slate-500")
                                    with ui.row().classes("items-center gap-1 shrink-0"):
                                        if venue.supervisor_phone:
                                            v_wa = container.communication_service.format_whatsapp_number(
                                                venue.supervisor_phone
                                            )
                                            if v_wa:
                                                ui.button(
                                                    icon="chat",
                                                    on_click=lambda n=v_wa: ui.navigate.to(
                                                        f"https://wa.me/{n}",
                                                        new_tab=True,
                                                    ),
                                                ).props(
                                                    "flat round dense size=xs color=green-7"
                                                ).tooltip("WhatsApp do Preceptor")
                                        if venue.supervisor_email:
                                            ui.button(
                                                icon="mail_outline",
                                                on_click=lambda em=venue.supervisor_email: ui.navigate.to(
                                                    f"mailto:{em}", new_tab=True
                                                ),
                                            ).props(
                                                "flat round dense size=xs color=blue-7"
                                            ).tooltip("E-mail do Preceptor")
                            else:
                                with ui.row().classes(
                                    "items-center gap-2 py-3 text-amber-700"
                                ):
                                    ui.icon("warning_amber", size="sm")
                                    ui.label(
                                        "Estagiário ainda não vinculado a um local."
                                    ).classes("text-xs font-medium")

                        # Right: Schedule & Contract Validity ONLY (Separated from Documents)
                        with ui.card().classes(
                            "p-4 bg-white border border-slate-200/80 rounded-xl shadow-none gap-2.5 min-w-0"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center pb-1.5 border-b border-slate-100"
                            ):
                                with ui.row().classes("items-center gap-1.5"):
                                    ui.icon("schedule", size="16px").classes(
                                        "text-blue-700"
                                    )
                                    ui.label("VIGÊNCIA E ESCALA").classes(
                                        "text-xs font-bold text-slate-700 tracking-wider"
                                    )
                                days_rem = fresh_intern.days_remaining
                                if days_rem is not None and fresh_intern.is_active:
                                    ui.badge(
                                        f"{days_rem} dias restantes"
                                        if days_rem >= 0
                                        else "Prazo encerrado",
                                        color="amber-1"
                                        if fresh_intern.is_near_deadline
                                        else "blue-1",
                                        text_color="amber-9"
                                        if fresh_intern.is_near_deadline
                                        else "blue-9",
                                    ).classes("text-[10px] font-bold px-2 py-0.5 rounded")

                            with ui.row().classes(
                                "w-full justify-between text-xs text-slate-700"
                            ):
                                ui.label(
                                    f"Período: {fresh_intern.formatted_start_date} a {fresh_intern.formatted_end_date}"
                                ).classes("font-semibold")
                                ui.label(f"{fresh_intern.time_progress_percent}%").classes(
                                    "font-bold text-slate-500"
                                )

                            ui.linear_progress(
                                value=fresh_intern.time_progress_percent / 100.0,
                                show_value=False,
                                color="blue-7",
                            ).props("rounded size=6px track-color=grey-3").classes(
                                "w-full"
                            )

                            with ui.row().classes(
                                "w-full items-center gap-4 pt-1 text-xs text-slate-600 flex-wrap"
                            ):
                                with ui.row().classes("items-center gap-1"):
                                    ui.icon("date_range", size="14px").classes(
                                        "text-slate-400"
                                    )
                                    ui.label(
                                        f"Dias: {fresh_intern.working_days or 'Não inf.'}"
                                    )
                                with ui.row().classes("items-center gap-1"):
                                    ui.icon("access_time", size="14px").classes(
                                        "text-slate-400"
                                    )
                                    ui.label(
                                        f"Horário: {fresh_intern.working_hours or 'Não inf.'}"
                                    )

                    # 4. Dedicated Mandatory Documents Card (Separated from Schedule)
                    with ui.card().classes(
                        "w-full p-4 bg-white border border-slate-200/80 rounded-xl shadow-none gap-2.5 min-w-0"
                    ):
                        with ui.row().classes(
                            "w-full justify-between items-center pb-1.5 border-b border-slate-100"
                        ):
                            with ui.row().classes("items-center gap-1.5"):
                                ui.icon("folder_shared", size="16px").classes(
                                    "text-emerald-700" if not pending_docs and docs else "text-amber-600"
                                )
                                ui.label("SITUAÇÃO DOCUMENTAL (OBRIGATÓRIOS)").classes(
                                    "text-xs font-bold text-slate-700 tracking-wider"
                                )
                            ui.button(
                                "Auditar Documentos",
                                icon="verified",
                                on_click=lambda: open_document_dialog(
                                    intern=fresh_intern,
                                    service=container.document_service,
                                    on_close=notify_and_refresh,
                                ),
                            ).props("flat dense no-caps size=xs color=primary").classes(
                                "font-semibold"
                            )

                        if not docs:
                            ui.label(
                                "Nenhum documento obrigatório gerado para este aluno."
                            ).classes("text-xs text-slate-400 py-1")
                        else:
                            with ui.row().classes("w-full gap-2 flex-wrap"):
                                for d in docs:
                                    is_ok = (d.status or "").lower() == "aprovado"
                                    is_rej = (d.status or "").lower() == "reprovado"
                                    chip_bg = (
                                        "bg-emerald-50 border-emerald-200 text-emerald-900"
                                        if is_ok
                                        else (
                                            "bg-rose-50 border-rose-200 text-rose-900"
                                            if is_rej
                                            else "bg-amber-50 border-amber-200 text-amber-900"
                                        )
                                    )
                                    chip_icon = (
                                        "check_circle"
                                        if is_ok
                                        else ("cancel" if is_rej else "schedule")
                                    )
                                    with ui.row().classes(
                                        f"items-center gap-1.5 px-2.5 py-1 rounded-lg border text-xs font-medium {chip_bg}"
                                    ):
                                        ui.icon(chip_icon, size="14px")
                                        ui.label(
                                            f"{d.document_name}: {d.status or 'Pendente'}"
                                        )

                    # 5. Recent Incidents / Observations & Meetings (With full word wrapping)
                    with ui.grid(columns=1).classes("w-full md:grid-cols-2 gap-3"):
                        # Recent Observations / Incidents
                        with ui.card().classes(
                            "p-4 bg-white border border-slate-200/80 rounded-xl shadow-none gap-2 min-w-0 overflow-hidden"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center pb-1 border-b border-slate-100"
                            ):
                                ui.label("ÚLTIMAS OCORRÊNCIAS / OBSERVAÇÕES").classes(
                                    "text-xs font-bold text-slate-700 tracking-wider"
                                )
                                ui.button(
                                    "Nova / Ver Todas",
                                    icon="add",
                                    on_click=lambda: open_observation_dialog(
                                        intern=fresh_intern,
                                        service=container.observation_service,
                                        on_close=notify_and_refresh,
                                    ),
                                ).props("flat dense no-caps size=xs color=primary")

                            if not observations:
                                ui.label(
                                    "Nenhuma observação ou ocorrência registrada."
                                ).classes("text-xs text-slate-400 py-3")
                            else:
                                for obs in observations[:3]:
                                    is_inc = bool(getattr(obs, "is_incident", False))
                                    att = getattr(obs, "attachment_path", None)
                                    with ui.column().classes(
                                        "w-full min-w-0 overflow-hidden p-2.5 rounded-lg border "
                                        + (
                                            "bg-rose-50/50 border-rose-200"
                                            if is_inc
                                            else "bg-slate-50 border-slate-200/70"
                                        )
                                        + " gap-1"
                                    ):
                                        with ui.row().classes(
                                            "w-full justify-between items-center gap-2"
                                        ):
                                            ui.badge(
                                                "⚠️ Ocorrência"
                                                if is_inc
                                                else "Observação",
                                                color="red-1" if is_inc else "blue-1",
                                                text_color="red-9"
                                                if is_inc
                                                else "blue-9",
                                            ).classes("text-[10px] font-bold px-1.5")
                                            ui.label(
                                                (obs.last_update or "")[:10]
                                            ).classes("text-[10px] text-slate-400")
                                        ui.label(obs.observation).classes(
                                            "w-full text-xs text-slate-700 whitespace-pre-wrap break-words leading-relaxed"
                                        ).style("overflow-wrap: anywhere; word-break: break-word;")
                                        if att:
                                            ui.button(
                                                "Baixar Documento Anexo",
                                                icon="attach_file",
                                                on_click=lambda f=att: ui.download(
                                                    str(attachments_dir / f), filename=f
                                                ),
                                            ).props(
                                                "flat dense no-caps size=xs color=primary"
                                            ).classes("self-start")

                        # Recent Supervision Meetings
                        with ui.card().classes(
                            "p-4 bg-white border border-slate-200/80 rounded-xl shadow-none gap-2 min-w-0 overflow-hidden"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center pb-1 border-b border-slate-100"
                            ):
                                ui.label("ÚLTIMAS REUNIÕES DE SUPERVISÃO").classes(
                                    "text-xs font-bold text-slate-700 tracking-wider"
                                )
                                ui.button(
                                    "Registrar / Ver Todas",
                                    icon="add",
                                    on_click=lambda: open_meeting_dialog(
                                        intern=fresh_intern,
                                        service=container.meeting_service,
                                        on_close=notify_and_refresh,
                                    ),
                                ).props("flat dense no-caps size=xs color=primary")

                            if not meetings:
                                ui.label(
                                    "Nenhuma reunião de supervisão registrada."
                                ).classes("text-xs text-slate-400 py-3")
                            else:
                                for m in list(reversed(meetings))[:3]:
                                    with ui.row().classes(
                                        "w-full min-w-0 p-2.5 rounded-lg bg-slate-50 border border-slate-200/70 items-start justify-between gap-2 no-wrap"
                                    ):
                                        with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                                            ui.label(
                                                m.meeting_topic or "Sem pauta"
                                            ).classes(
                                                "w-full text-xs font-semibold text-slate-800 whitespace-pre-wrap break-words"
                                            ).style("overflow-wrap: anywhere;")
                                            ui.label(m.meeting_date or "").classes(
                                                "text-[11px] text-slate-400"
                                            )
                                        ui.badge(
                                            "Presente"
                                            if m.is_intern_present
                                            else "Ausente",
                                            color="green-1"
                                            if m.is_intern_present
                                            else "red-1",
                                            text_color="green-9"
                                            if m.is_intern_present
                                            else "red-9",
                                        ).classes(
                                            "text-[10px] font-bold px-2 py-0.5 rounded shrink-0"
                                        )

                # 6. Footer Actions
                with ui.row().classes(
                    "w-full px-5 sm:px-6 py-3 bg-white border-t border-slate-200 justify-between items-center flex-wrap gap-2"
                ):
                    ui.button(
                        "Gerar Relatório Individual (PDF)",
                        icon="picture_as_pdf",
                        on_click=lambda: open_report_dialog(
                            intern=fresh_intern, container=container
                        ),
                    ).props("outline no-caps color=negative size=sm").classes("px-3")

                    with ui.row().classes("items-center gap-2"):
                        ui.button(
                            "Registrar Ocorrência / Anexo",
                            icon="assignment_late",
                            on_click=lambda: open_observation_dialog(
                                intern=fresh_intern,
                                service=container.observation_service,
                                on_close=notify_and_refresh,
                            ),
                        ).props("unelevated no-caps color=primary size=sm").classes(
                            "px-3 font-semibold"
                        )
                        ui.button("Fechar", on_click=dialog.close).props(
                            "flat no-caps color=grey-7 size=sm"
                        )

        render_dossier()

    dialog.open()


def open_venue_quick_view(
    venue: Venue,
    container: ServiceContainer,
    on_change: Optional[Callable] = None,
):
    """Opens the 360° Quick View Dossier for an internship venue, listing all allocated interns."""
    if not venue.venue_id:
        return

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-2xl p-0 rounded-2xl overflow-hidden shadow-2xl border border-slate-200"
    ):
        content_box = ui.column().classes("w-full gap-0")

        def notify_and_refresh():
            render_venue_dossier()
            if on_change:
                on_change()

        def render_venue_dossier():
            content_box.clear()
            fresh_venue = (
                container.venue_service.get_by_id(venue.venue_id)
                if venue.venue_id
                else venue
            ) or venue

            all_interns = container.intern_service.get_all_interns()
            venue_interns = [
                i for i in all_interns if i.venue_id == fresh_venue.venue_id
            ]
            active_interns = [i for i in venue_interns if i.is_active]
            inactive_interns = [i for i in venue_interns if not i.is_active]

            with content_box:
                # Header Banner
                with ui.row().classes(
                    "w-full px-5 sm:px-6 py-4 bg-slate-900 text-white items-start sm:items-center justify-between gap-3"
                ):
                    with ui.row().classes("items-center gap-3 min-w-0 flex-1"):
                        ui.avatar(
                            "domain",
                            color="blue-7",
                            text_color="white",
                            size="lg",
                        ).classes("rounded-xl shrink-0")
                        with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                            ui.label(fresh_venue.venue_name).classes(
                                "text-base sm:text-lg font-extrabold text-white truncate"
                            )
                            ui.label(
                                fresh_venue.address or "Endereço não cadastrado"
                            ).classes("text-xs text-slate-300 truncate")
                            ui.label(
                                f"Preceptor: {fresh_venue.supervisor_name or 'Não informado'} • {fresh_venue.supervisor_phone or 'Sem telefone'}"
                            ).classes("text-xs text-blue-200 font-medium")

                    with ui.row().classes("items-center gap-1.5 shrink-0"):
                        if fresh_venue.supervisor_phone:
                            wa = container.communication_service.format_whatsapp_number(
                                fresh_venue.supervisor_phone
                            )
                            if wa:
                                ui.button(
                                    icon="chat",
                                    on_click=lambda n=wa: ui.navigate.to(
                                        f"https://wa.me/{n}", new_tab=True
                                    ),
                                ).props(
                                    "unelevated round dense size=sm color=green-6"
                                ).tooltip("WhatsApp do Preceptor")

                        if fresh_venue.supervisor_email:
                            ui.button(
                                icon="mail_outline",
                                on_click=lambda em=fresh_venue.supervisor_email: ui.navigate.to(
                                    f"mailto:{em}", new_tab=True
                                ),
                            ).props(
                                "unelevated round dense size=sm color=blue-7"
                            ).tooltip("E-mail do Preceptor")

                        ui.button(
                            icon="edit",
                            on_click=lambda: open_venue_dialog(
                                venue_service=container.venue_service,
                                venue=fresh_venue,
                                on_success=notify_and_refresh,
                            ),
                        ).props("flat round dense size=sm color=white").tooltip(
                            "Editar Local"
                        )

                        ui.button(icon="close", on_click=dialog.close).props(
                            "flat round dense size=sm color=grey-4"
                        )

                # Body: Summary + Interns List
                with ui.column().classes(
                    "w-full px-5 sm:px-6 py-4 gap-4 max-h-[70vh] overflow-y-auto bg-slate-50"
                ):
                    with ui.grid(columns=2).classes("w-full gap-3"):
                        with ui.card().classes(
                            "p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-none gap-0.5"
                        ):
                            ui.label("ESTAGIÁRIOS ATIVOS NO LOCAL").classes(
                                "text-[10px] font-bold text-slate-400 tracking-wider"
                            )
                            ui.label(str(len(active_interns))).classes(
                                "text-2xl font-extrabold text-blue-700"
                            )

                        with ui.card().classes(
                            "p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-none gap-0.5"
                        ):
                            ui.label("HISTÓRICO / CONCLUÍDOS").classes(
                                "text-[10px] font-bold text-slate-400 tracking-wider"
                            )
                            ui.label(str(len(inactive_interns))).classes(
                                "text-2xl font-extrabold text-slate-700"
                            )

                    ui.label(
                        f"Relação de Estagiários Vinculados ({len(venue_interns)})"
                    ).classes(
                        "text-xs font-bold text-slate-700 uppercase tracking-wider pt-1"
                    )

                    if not venue_interns:
                        with ui.card().classes(
                            "w-full py-10 bg-white border border-dashed border-slate-200 rounded-xl items-center justify-center gap-1 shadow-none"
                        ):
                            ui.icon("person_off", size="lg").classes("text-slate-300")
                            ui.label(
                                "Nenhum estagiário vinculado a esta instituição."
                            ).classes("text-xs text-slate-500")
                    else:
                        for student in venue_interns:
                            with ui.card().classes(
                                "w-full p-3.5 bg-white border border-slate-200/80 rounded-xl shadow-none flex-row items-center justify-between gap-3 hover:border-blue-400 transition-all"
                            ):
                                with ui.row().classes(
                                    "items-center gap-3 min-w-0 flex-1"
                                ):
                                    ui.avatar(
                                        _get_initials(student.name),
                                        color="blue-1"
                                        if student.is_active
                                        else "grey-3",
                                        text_color="blue-9"
                                        if student.is_active
                                        else "grey-7",
                                        size="md",
                                    ).classes("font-bold text-xs shrink-0")
                                    with ui.column().classes("gap-0.5 min-w-0 flex-1"):
                                        with ui.row().classes(
                                            "items-center gap-2 flex-wrap"
                                        ):
                                            ui.label(student.name).classes(
                                                "font-bold text-sm text-slate-900 truncate"
                                            )
                                            create_status_badge(student.status)
                                        ui.label(
                                            f"RA: {student.registration_number} • Semestre: {student.term} • {student.working_days or 'Dias N/I'} ({student.working_hours or 'Horário N/I'})"
                                        ).classes("text-xs text-slate-500 truncate")

                                ui.button(
                                    "Dossiê 360°",
                                    icon="visibility",
                                    on_click=lambda s=student: (
                                        dialog.close(),
                                        open_intern_quick_view(
                                            s, container, on_change=on_change
                                        ),
                                    ),
                                ).props(
                                    "unelevated dense no-caps size=sm color=blue-1 text-color=blue-9"
                                ).classes("px-3 font-semibold shrink-0")

                # Footer
                with ui.row().classes(
                    "w-full px-6 py-3 bg-white border-t border-slate-200 justify-end"
                ):
                    ui.button("Fechar", on_click=dialog.close).props(
                        "flat no-caps color=grey-7"
                    )

        render_venue_dossier()

    dialog.open()
