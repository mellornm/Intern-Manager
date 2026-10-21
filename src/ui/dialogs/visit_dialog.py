"""
Technical Visits dialog for NiceGUI with photo upload and preview.
"""

from datetime import date
from typing import Callable, Optional
from nicegui import ui

from config import USER_DATA_ROOT, TEMP_DIR
from core.models.intern import Intern
from core.models.visit import Visit
from services.venue_service import VenueService
from services.visit_service import VisitService


def open_visit_dialog(
    intern: Intern,
    service: VisitService,
    venue_service: VenueService,
    on_close: Optional[Callable] = None,
):
    """Opens modal to manage technical visits and photos for an intern."""
    venues = venue_service.get_all()
    venue_dict = {v.venue_id: v.venue_name for v in venues if v.venue_id is not None}
    venue_dict[0] = "Local Não Especificado"

    photos_dir = USER_DATA_ROOT / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-3xl p-6 dialog-card"):
        with ui.row().classes("w-full items-center justify-between pb-3 border-b border-slate-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("pin_drop", color="primary", size="md")
                with ui.column().classes("gap-0"):
                    ui.label(f"Visitas Técnicas: {intern.name}").classes("text-xl font-bold text-slate-800")
                    ui.label("Supervisão in loco e registro fotográfico").classes("text-xs text-slate-500")
            ui.button(icon="close", on_click=dialog.close).props("flat round dense size=sm")

        list_container = ui.column().classes("w-full max-h-72 overflow-y-auto gap-2 py-2")

        def refresh_visits():
            list_container.clear()
            if not intern.intern_id:
                return

            visits = service.get_by_intern_id(intern.intern_id)

            with list_container:
                if not visits:
                    with ui.column().classes("w-full items-center py-6 gap-1"):
                        ui.icon("location_off", size="lg").classes("text-slate-300")
                        ui.label("Nenhuma visita técnica registrada.").classes("text-xs text-slate-500")
                    return

                for v in reversed(visits):
                    v_name = venue_dict.get(v.venue_id, "Local Não Informado")
                    with ui.card().classes("w-full p-3 bg-white border border-slate-200 gap-2"):
                        with ui.row().classes("w-full justify-between items-center"):
                            with ui.row().classes("items-center gap-2"):
                                ui.badge(v.visit_date or "Sem data", color="blue-7").classes("text-xs font-semibold")
                                ui.label(f"📍 {v_name}").classes("text-xs font-bold text-slate-700")

                            with ui.row().classes("items-center gap-1"):
                                if v.photo_path:
                                    ui.button(
                                        icon="image",
                                        on_click=lambda photo=v.photo_path: open_photo_preview(photo),
                                    ).props("flat round dense size=xs color=primary").tooltip("Ver Foto")

                                ui.button(
                                    icon="delete",
                                    on_click=lambda vis=v: handle_delete_visit(vis),
                                ).props("flat round dense size=xs color=negative").tooltip("Excluir Visita")

                        if v.observation:
                            ui.label(v.observation).classes("text-sm text-slate-800 whitespace-pre-wrap")

        def handle_delete_visit(visit_obj):
            if visit_obj:
                service.delete_visit(visit_obj)
                ui.notify("Visita técnica excluída.", color="info")
                refresh_visits()

        def open_photo_preview(filename: str):
            photo_file = photos_dir / filename
            if not photo_file.exists():
                ui.notify("Arquivo da foto não encontrado no servidor.", color="warning")
                return

            with ui.dialog() as p_dialog, ui.card().classes("p-4 dialog-card max-w-2xl"):
                with ui.row().classes("w-full justify-between items-center pb-2"):
                    ui.label("Registro Fotográfico").classes("font-bold text-slate-800")
                    ui.button(icon="close", on_click=p_dialog.close).props("flat round dense size=sm")

                ui.image(photo_file).classes("rounded-lg max-h-96 object-contain")
            p_dialog.open()

        # Add new visit form
        with ui.column().classes("w-full pt-3 border-t border-slate-200 gap-2"):
            ui.label("Nova Visita Técnica").classes("text-xs font-bold text-slate-700 uppercase tracking-wider")

            with ui.grid(columns=2).classes("w-full gap-3"):
                date_input = ui.input("Data da Visita", value=date.today().isoformat()).classes("w-full").props("dense outlined")
                with date_input.add_slot("append"):
                    ui.icon("event").classes("cursor-pointer")
                    with ui.menu():
                        ui.date().bind_value(date_input)

                venue_select = ui.select(
                    label="Local da Visita",
                    options=venue_dict,
                    value=intern.venue_id or 0,
                ).classes("w-full").props("dense outlined")

            notes_input = ui.textarea(
                label="Observações / Avaliação da Visita",
                placeholder="Descreva as condições de trabalho, orientações passadas e estrutura...",
            ).classes("w-full").props("outlined rows=2")

            uploaded_photo_filename = {"name": ""}

            async def handle_photo_upload(e):
                content = e.content.read()
                temp_file = TEMP_DIR / e.name
                with open(temp_file, "wb") as f:
                    f.write(content)

                v_name = venue_dict.get(venue_select.value, "Local")
                saved_name = service.save_photo(
                    original_path_str=str(temp_file),
                    intern_name=intern.name,
                    venue_name=v_name,
                    visit_date=date_input.value,
                )
                uploaded_photo_filename["name"] = saved_name
                ui.notify(f"Foto '{e.name}' carregada com sucesso!", color="positive")
                try:
                    temp_file.unlink(missing_ok=True)
                except Exception:
                    pass

            with ui.row().classes("w-full items-center justify-between"):
                with ui.row().classes("items-center gap-2"):
                    ui.upload(
                        label="Anexar Foto",
                        on_upload=handle_photo_upload,
                        auto_upload=True,
                        max_files=1,
                    ).props('accept="image/*" flat size=sm').classes("max-w-xs")

                def handle_add_visit():
                    if not intern.intern_id:
                        return

                    selected_vid = venue_select.value if venue_select.value != 0 else None
                    if not selected_vid:
                        ui.notify("Selecione um local de estágio válido para a visita.", color="warning")
                        return

                    new_visit = Visit(
                        intern_id=intern.intern_id,
                        venue_id=selected_vid,
                        visit_date=date_input.value,
                        observation=notes_input.value or "",
                        photo_path=uploaded_photo_filename["name"] or None,
                    )
                    try:
                        service.add_new_visit(new_visit)
                        notes_input.value = ""
                        uploaded_photo_filename["name"] = ""
                        ui.notify("Visita técnica registrada com sucesso!", color="positive")
                        refresh_visits()
                    except Exception as e:
                        ui.notify(f"Erro ao salvar visita: {e}", color="negative")

                ui.button("Registrar Visita", icon="add", on_click=handle_add_visit).props("color=primary size=sm")

        refresh_visits()

        with ui.row().classes("w-full justify-end pt-3 border-t border-slate-200 mt-2"):
            ui.button("Fechar", on_click=dialog.close).props("flat color=grey")

    if on_close:
        dialog.on("hide", on_close)

    dialog.open()
