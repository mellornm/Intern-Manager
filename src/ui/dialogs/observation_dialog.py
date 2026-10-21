"""
Pedagogical Observations and Incident Reports Dialog for NiceGUI.
Supports categorizing records as standard observations or critical incidents
(e.g., sharps/needlestick injury, medical certificates) and attaching files (PDF/Images).
"""

from typing import Callable, Optional
from nicegui import ui

from config import TEMP_DIR, USER_DATA_ROOT
from core.models.intern import Intern
from core.models.observation import Observation
from services.observation_service import ObservationService

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def open_observation_dialog(
    intern: Intern,
    service: ObservationService,
    on_close: Optional[Callable] = None,
):
    """Opens modal to manage pedagogical observations, incidents, and medical attachments."""
    attachments_dir = USER_DATA_ROOT / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    with ui.dialog() as dialog, ui.card().classes(
        "w-full max-w-2xl p-0 rounded-2xl overflow-hidden shadow-2xl border border-slate-200"
    ):
        # Modal Header
        with ui.row().classes(
            "w-full px-5 sm:px-6 py-4 bg-slate-50 border-b border-slate-200 items-center justify-between"
        ):
            with ui.row().classes("items-center gap-3"):
                ui.avatar(
                    "assignment_late",
                    color="blue-1",
                    text_color="primary",
                    size="md",
                ).classes("rounded-xl")
                with ui.column().classes("gap-0"):
                    ui.label(f"Observações e Ocorrências: {intern.name}").classes(
                        "text-base sm:text-lg font-bold text-slate-900"
                    )
                    ui.label(
                        "Anotações pedagógicas, intercorrências médicas/acidentes e documentos anexos"
                    ).classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props(
                "flat round dense size=sm color=grey-7"
            )

        with ui.column().classes("w-full px-5 sm:px-6 py-4 gap-4 max-h-[80vh] overflow-y-auto"):
            # Container for observation/incident timeline
            timeline_container = ui.column().classes("w-full gap-2.5")

            def open_attachment_preview_or_download(filename: str):
                file_path = attachments_dir / filename
                if not file_path.exists():
                    ui.notify("Arquivo anexo não encontrado no disco.", color="warning")
                    return

                ext = file_path.suffix.lower()
                if ext in IMAGE_EXTENSIONS:
                    with ui.dialog() as p_dialog, ui.card().classes(
                        "p-4 rounded-2xl max-w-2xl w-full"
                    ):
                        with ui.row().classes("w-full justify-between items-center pb-2"):
                            ui.label("Visualização do Anexo").classes(
                                "font-bold text-slate-800 text-sm"
                            )
                            with ui.row().classes("items-center gap-1"):
                                ui.button(
                                    "Baixar",
                                    icon="download",
                                    on_click=lambda: ui.download(
                                        str(file_path), filename=filename
                                    ),
                                ).props("flat dense no-caps color=primary size=sm")
                                ui.button(icon="close", on_click=p_dialog.close).props(
                                    "flat round dense size=sm"
                                )
                        ui.image(file_path).classes("rounded-lg max-h-96 object-contain")
                    p_dialog.open()
                else:
                    ui.notify("Iniciando download do documento anexo...", color="info")
                    ui.download(str(file_path), filename=filename)

            def open_attach_to_existing_dialog(obs_obj: Observation):
                with ui.dialog() as att_dialog, ui.card().classes(
                    "p-5 rounded-2xl max-w-md w-full gap-3"
                ):
                    with ui.row().classes("w-full justify-between items-center"):
                        ui.label("Anexar Documento ao Registro").classes(
                            "font-bold text-slate-900 text-base"
                        )
                        ui.button(icon="close", on_click=att_dialog.close).props(
                            "flat round dense size=sm"
                        )

                    ui.label(
                        "Envie um PDF, atestado, ficha de notificação ou foto para vincular a este registro."
                    ).classes("text-xs text-slate-500")

                    incident_chk = ui.checkbox(
                        "Marcar este registro como ⚠️ Ocorrência / Intercorrência",
                        value=bool(obs_obj.is_incident),
                    ).classes("text-xs font-semibold text-rose-700")

                    async def handle_existing_upload(e):
                        content = e.content.read()
                        temp_file = TEMP_DIR / e.name
                        with open(temp_file, "wb") as f:
                            f.write(content)
                        try:
                            saved_name = service.save_attachment(
                                original_path_str=str(temp_file),
                                intern_name=intern.name,
                            )
                            obs_obj.attachment_path = saved_name
                            obs_obj.is_incident = bool(incident_chk.value)
                            service.update_observation(obs_obj)
                            ui.notify("Documento anexado ao registro!", color="positive")
                            att_dialog.close()
                            refresh_observations()
                        except Exception as err:
                            ui.notify(f"Erro ao anexar arquivo: {err}", color="negative")
                        finally:
                            temp_file.unlink(missing_ok=True)

                    ui.upload(
                        label="Selecione o arquivo (PDF, Imagem, etc.)",
                        auto_upload=True,
                        max_files=1,
                        on_upload=handle_existing_upload,
                    ).props(
                        'accept=".pdf,.png,.jpg,.jpeg,.webp,.doc,.docx" flat bordered color=primary'
                    ).classes("w-full")

                att_dialog.open()

            def toggle_incident_status(obs_obj: Observation):
                obs_obj.is_incident = not bool(obs_obj.is_incident)
                service.update_observation(obs_obj)
                ui.notify(
                    "Marcado como Ocorrência!"
                    if obs_obj.is_incident
                    else "Convertido para Observação comum.",
                    color="info",
                )
                refresh_observations()

            def refresh_observations():
                timeline_container.clear()
                if not intern.intern_id:
                    return

                obs_list = service.get_by_intern_id(intern.intern_id)

                with timeline_container:
                    if not obs_list:
                        with ui.column().classes(
                            "w-full items-center py-8 gap-1.5 bg-slate-50/70 rounded-xl border border-dashed border-slate-200"
                        ):
                            ui.icon("chat_bubble_outline", size="lg").classes(
                                "text-slate-300"
                            )
                            ui.label(
                                "Nenhuma observação ou ocorrência registrada."
                            ).classes("text-xs font-medium text-slate-500")
                        return

                    for obs in obs_list:
                        is_inc = bool(getattr(obs, "is_incident", False))
                        att_name = getattr(obs, "attachment_path", None)
                        date_display = (
                            obs.last_update[:16] if obs.last_update else "Data não inf."
                        )

                        card_style = (
                            "bg-rose-50/50 border-rose-200 border-l-4 border-l-rose-600"
                            if is_inc
                            else "bg-white border-slate-200/80 border-l-4 border-l-blue-600"
                        )

                        with ui.card().classes(
                            f"w-full min-w-0 overflow-hidden p-3.5 rounded-xl border {card_style} shadow-none gap-2"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center gap-2 flex-wrap"
                            ):
                                with ui.row().classes("items-center gap-2"):
                                    if is_inc:
                                        ui.badge(
                                            "⚠️ OCORRÊNCIA / INTERCORRÊNCIA",
                                            color="red-1",
                                            text_color="red-9",
                                        ).classes(
                                            "text-[10px] font-bold px-2 py-0.5 rounded border border-red-200"
                                        )
                                    else:
                                        ui.badge(
                                            "OBSERVAÇÃO PEDAGÓGICA",
                                            color="blue-1",
                                            text_color="blue-9",
                                        ).classes(
                                            "text-[10px] font-bold px-2 py-0.5 rounded border border-blue-200"
                                        )
                                    ui.label(date_display).classes(
                                        "text-[11px] font-medium text-slate-400"
                                    )

                                with ui.row().classes("items-center gap-1"):
                                    ui.button(
                                        icon="warning_amber" if not is_inc else "notes",
                                        on_click=lambda o=obs: toggle_incident_status(o),
                                    ).props(
                                        "flat round dense size=xs color=amber-9"
                                    ).tooltip(
                                        "Marcar como Ocorrência"
                                        if not is_inc
                                        else "Mudar para Observação Comum"
                                    )

                                    ui.button(
                                        icon="attach_file",
                                        on_click=lambda o=obs: open_attach_to_existing_dialog(
                                            o
                                        ),
                                    ).props(
                                        "flat round dense size=xs color=primary"
                                    ).tooltip("Anexar / Substituir Documento neste registro")

                                    ui.button(
                                        icon="delete_outline",
                                        on_click=lambda o_id=obs.observation_id: handle_delete_obs(
                                            o_id
                                        ),
                                    ).props(
                                        "flat round dense size=xs color=negative"
                                    ).tooltip("Excluir Registro")

                            ui.label(obs.observation).classes(
                                "w-full text-sm text-slate-800 whitespace-pre-wrap break-words leading-relaxed"
                            ).style("overflow-wrap: anywhere; word-break: break-word;")

                            if att_name:
                                with ui.row().classes(
                                    "w-full items-center justify-between px-3 py-1.5 rounded-lg bg-white/90 border border-slate-200 mt-1"
                                ):
                                    with ui.row().classes("items-center gap-2 min-w-0"):
                                        ui.icon(
                                            "description", size="16px", color="primary"
                                        )
                                        ui.label(f"Anexo: {att_name}").classes(
                                            "text-xs font-semibold text-slate-700 truncate max-w-xs"
                                        )
                                    with ui.row().classes("items-center gap-1"):
                                        if (attachments_dir / att_name).suffix.lower() in IMAGE_EXTENSIONS:
                                            ui.button(
                                                "Visualizar",
                                                icon="visibility",
                                                on_click=lambda f=att_name: open_attachment_preview_or_download(
                                                    f
                                                ),
                                            ).props(
                                                "flat dense no-caps size=xs color=primary"
                                            )
                                        ui.button(
                                            "Baixar Documento",
                                            icon="download",
                                            on_click=lambda f=att_name: ui.download(
                                                str(attachments_dir / f), filename=f
                                            ),
                                        ).props(
                                            "unelevated dense no-caps size=xs color=blue-1 text-color=blue-9"
                                        ).classes("px-2 font-semibold")

            def handle_delete_obs(obs_id):
                if obs_id:
                    service.delete_observation(obs_id)
                    ui.notify("Registro excluído.", color="info")
                    refresh_observations()

            # Add New Observation / Incident Form
            with ui.card().classes(
                "w-full p-4 bg-slate-50 border border-slate-200/90 rounded-xl shadow-none gap-3"
            ):
                with ui.row().classes(
                    "w-full items-center justify-between gap-2 flex-wrap"
                ):
                    ui.label("Novo Registro").classes(
                        "text-xs font-bold text-slate-700 uppercase tracking-wider"
                    )
                    incident_switch = (
                        ui.switch(
                            "Classificar como ⚠️ Ocorrência / Intercorrência (Acidente, Atestado)",
                            value=False,
                        )
                        .props("dense color=negative")
                        .classes("text-xs font-semibold text-slate-700")
                    )

                obs_input = (
                    ui.textarea(
                        placeholder="Descreva o acompanhamento pedagógico ou relate a ocorrência (ex: acidente com perfurocortante, conduta adotada, atestado médico)...",
                    )
                    .classes("w-full bg-white")
                    .props("outlined dense rows=3 hide-bottom-space")
                )

                uploaded_attachment = {"name": "", "original": ""}

                attachment_badge_row = ui.row().classes(
                    "w-full items-center justify-between px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200"
                )
                attachment_badge_row.set_visibility(False)

                with attachment_badge_row:
                    att_label = ui.label("").classes(
                        "text-xs font-semibold text-blue-900 truncate"
                    )

                    def clear_pending_attachment():
                        if uploaded_attachment["name"]:
                            service._delete_physical_attachment(
                                uploaded_attachment["name"]
                            )
                        uploaded_attachment["name"] = ""
                        uploaded_attachment["original"] = ""
                        attachment_badge_row.set_visibility(False)

                    ui.button(
                        icon="close", on_click=clear_pending_attachment
                    ).props("flat round dense size=xs color=blue-9")

                async def handle_file_upload(e):
                    content = e.content.read()
                    temp_file = TEMP_DIR / e.name
                    with open(temp_file, "wb") as f:
                        f.write(content)

                    try:
                        saved_name = service.save_attachment(
                            original_path_str=str(temp_file),
                            intern_name=intern.name,
                        )
                        uploaded_attachment["name"] = saved_name
                        uploaded_attachment["original"] = e.name
                        att_label.set_text(f"📎 Documento pronto para anexar: {e.name}")
                        attachment_badge_row.set_visibility(True)
                        ui.notify(
                            f"Arquivo '{e.name}' carregado! Clique em Salvar Registro para confirmar.",
                            color="positive",
                        )
                    except Exception as err:
                        ui.notify(f"Erro no upload: {err}", color="negative")
                    finally:
                        temp_file.unlink(missing_ok=True)
                        uploader_widget.reset()

                with ui.row().classes(
                    "w-full items-center justify-between gap-3 flex-wrap"
                ):
                    uploader_widget = (
                        ui.upload(
                            label="Anexar Documento Médico / PDF / Foto",
                            on_upload=handle_file_upload,
                            auto_upload=True,
                            max_files=1,
                        )
                        .props(
                            'accept=".pdf,.png,.jpg,.jpeg,.webp,.doc,.docx" flat dense color=primary'
                        )
                        .classes("max-w-xs")
                    )

                    def handle_add_obs():
                        text = (obs_input.value or "").strip()
                        if not text:
                            ui.notify(
                                "Digite o relato da observação ou ocorrência.",
                                color="warning",
                            )
                            return

                        if not intern.intern_id:
                            return

                        new_obs = Observation(
                            intern_id=intern.intern_id,
                            observation=text,
                            is_incident=bool(incident_switch.value),
                            attachment_path=uploaded_attachment["name"] or None,
                        )
                        try:
                            service.add_new_observation(new_obs)
                            obs_input.value = ""
                            incident_switch.value = False
                            uploaded_attachment["name"] = ""
                            uploaded_attachment["original"] = ""
                            attachment_badge_row.set_visibility(False)
                            ui.notify(
                                "Registro salvo com sucesso!", color="positive"
                            )
                            refresh_observations()
                        except Exception as e:
                            ui.notify(f"Erro ao salvar: {e}", color="negative")

                    ui.button(
                        "Salvar Registro",
                        icon="send",
                        on_click=handle_add_obs,
                    ).props("unelevated no-caps color=primary").classes(
                        "px-4 font-semibold"
                    )

            refresh_observations()

        # Modal Footer
        with ui.row().classes(
            "w-full px-6 py-3 bg-slate-50 border-t border-slate-200 justify-end"
        ):
            ui.button("Fechar", on_click=dialog.close).props("flat no-caps color=grey-7")

    if on_close:
        dialog.on("hide", on_close)

    dialog.open()
