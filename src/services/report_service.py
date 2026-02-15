import os
from datetime import datetime

from PySide6.QtCore import QSettings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from core.models.document import Document
from core.models.evaluation_criteria import EvaluationCriteria
from core.models.grade import Grade
from core.models.intern import Intern
from core.models.meeting import Meeting
from core.models.observation import Observation
from core.models.venue import Venue
from core.models.visit import Visit


class ReportService:
    """
    PDF Report Generation Service using ReportLab.
    Goodbye 90s HTML, hello vector rendering.
    """

    def generate_pdf(
        self,
        filepath: str,
        intern: Intern,
        venue: Venue | None,
        criteria_list: list[EvaluationCriteria],
        grades: list[Grade],
        documents: list[Document],
        meetings: list[Meeting],
        observations: list[Observation],
        visits: list[Visit] | None = None,
    ):
        if visits is None:
            visits = []

        # --- 1. Load Settings (Keeping UI compatibility) ---
        settings = QSettings("MyOrganization", "InternManager2026")
        inst_name = settings.value("institution_name", "Instituição de Ensino")
        supervisor_name = settings.value("coordinator_name", "Coordenador não definido")
        city_state = settings.value("city_state", "Cidade - UF")
        logo_path = settings.value("logo_path", "")

        # Standard Colors
        PRIMARY_COLOR = colors.HexColor("#283593")
        TEXT_MAIN = colors.HexColor("#2C3E50")
        TEXT_MUTED = colors.HexColor("#7F8C8D")
        BG_LIGHT = colors.HexColor("#F8F9FA")
        BORDER_COLOR = colors.HexColor("#BDC3C7")

        # --- 2. Prepare Document Structure ---
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        styles = getSampleStyleSheet()

        # Custom Styles
        styles.add(
            ParagraphStyle(
                name="HeaderTitle",
                fontName="Helvetica-Bold",
                fontSize=14,
                textColor=PRIMARY_COLOR,
                alignment=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="HeaderSub",
                fontName="Helvetica",
                fontSize=9,
                textColor=TEXT_MUTED,
                alignment=2,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SectionTitle",
                fontName="Helvetica-Bold",
                fontSize=12,
                textColor=PRIMARY_COLOR,
                spaceBefore=15,
                spaceAfter=5,
            )
        )
        styles.add(
            ParagraphStyle(
                name="NormalText",
                fontName="Helvetica",
                fontSize=10,
                textColor=TEXT_MAIN,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SmallText",
                fontName="Helvetica",
                fontSize=8,
                textColor=TEXT_MUTED,
                alignment=1,
            )
        )

        Story = []  # List of elements that make up the PDF (Platypus flow)

        # --- 3. Header (Logo and Title) ---
        logo_img = ""
        if logo_path and os.path.exists(logo_path):
            try:
                # Maintain aspect ratio by limiting height
                logo_img = Image(logo_path, height=20 * mm, kind="proportional")
            except Exception:
                logo_img = ""

        header_text = [
            Paragraph(inst_name, styles["HeaderTitle"]),
            Paragraph("Relatório de Desempenho e Acompanhamento", styles["HeaderSub"]),
            Paragraph(f"Supervisor: {supervisor_name}", styles["HeaderSub"]),
        ]

        header_table = Table([[logo_img, header_text]], colWidths=[50 * mm, 130 * mm])
        header_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("LINEBELOW", (0, 0), (-1, -1), 1.5, PRIMARY_COLOR),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        Story.append(header_table)
        Story.append(Spacer(1, 5 * mm))

        # --- 4. Information Cards (Side by Side) ---
        venue_name = venue.venue_name if venue else "Não vinculado"
        venue_supervisor = (
            venue.supervisor_name
            if venue and venue.supervisor_name
            else "Não informado"
        )

        # Grades and Attendance Calculations
        grades_map = {
            g.criteria_id: g.value for g in grades if g.criteria_id is not None
        }
        total_score = sum(
            grades_map.get(c.criteria_id, 0.0) for c in criteria_list if c.criteria_id
        )
        is_approved = total_score >= 7.0
        status_text = "APROVADO" if is_approved else "EM ANÁLISE"
        status_color = (
            colors.HexColor("#27AE60") if is_approved else colors.HexColor("#E67E22")
        )

        total_meetings = len(meetings)
        present_meetings = sum(1 for m in meetings if m.is_intern_present)
        freq_percent = (
            (present_meetings / total_meetings * 100) if total_meetings > 0 else 0.0
        )

        col1 = [
            Paragraph("<b>Dados do Discente</b>", styles["NormalText"]),
            Paragraph(f"<b>Nome:</b> {intern.name}", styles["NormalText"]),
            Paragraph(
                f"<b>Registro:</b> {intern.registration_number}", styles["NormalText"]
            ),
            Paragraph(
                f"<b>Semestre:</b> {intern.term} | {intern.formatted_start_date} a {intern.formatted_end_date}",
                styles["NormalText"],
            ),
            Paragraph(
                f"<b>Carga:</b> {intern.working_days} ({intern.working_hours})",
                styles["NormalText"],
            ),
        ]

        col2 = [
            Paragraph("<b>Campo de Estágio</b>", styles["NormalText"]),
            Paragraph(f"<b>Local:</b> {venue_name}", styles["NormalText"]),
            Paragraph(f"<b>Preceptor:</b> {venue_supervisor}", styles["NormalText"]),
            Spacer(1, 3 * mm),
            Paragraph(
                f"<b>Status:</b> <font color='{status_color}'>{status_text}</font>",
                styles["NormalText"],
            ),
            Paragraph(
                f"<b>Média Final:</b> <b>{total_score:.1f}</b>", styles["NormalText"]
            ),
        ]

        info_table = Table([[col1, col2]], colWidths=[90 * mm, 90 * mm])
        info_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
                    ("BOX", (0, 0), (0, 0), 1, BORDER_COLOR),
                    ("BOX", (1, 0), (1, 0), 1, BORDER_COLOR),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        Story.append(info_table)

        # --- 5. Grades Board ---
        Story.append(Paragraph("Quadro de Avaliação e Notas", styles["SectionTitle"]))

        grades_data = [["Critério de Avaliação", "Peso Máx.", "Nota Obtida"]]
        for c in criteria_list:
            if c.criteria_id is None:
                continue
            val = grades_map.get(c.criteria_id, 0.0)
            color_str = "#27AE60" if val >= (c.weight * 0.7) else "#C0392B"

            p_criterio = Paragraph(c.name, styles["NormalText"])
            p_peso = Paragraph(f"{c.weight:.1f}", styles["NormalText"])
            p_nota = Paragraph(
                f"<b><font color='{color_str}'>{val:.1f}</font></b>",
                styles["NormalText"],
            )

            grades_data.append([p_criterio, p_peso, p_nota])

        t_grades = Table(grades_data, colWidths=[120 * mm, 30 * mm, 30 * mm])
        t_grades.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT),
                    ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY_COLOR),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        Story.append(t_grades)

        Story.append(
            Paragraph(
                f"Frequência em Reuniões: <b>{freq_percent:.1f}%</b> ({present_meetings} de {total_meetings})",
                ParagraphStyle(
                    "RightAligned", parent=styles["NormalText"], alignment=2
                ),
            )
        )

        # --- 6. Technical Visits ---
        Story.append(Paragraph("Auditoria e Visitas Técnicas", styles["SectionTitle"]))
        visits_data = [["Data", "Observações do Relatório de Campo"]]

        if not visits:
            visits_data.append(
                ["-", Paragraph("Nenhuma visita registrada.", styles["NormalText"])]
            )
        else:
            for v in visits:
                # Replaced duck typing with proper attribute access
                date_str = str(v.visit_date) if v.visit_date else "S/D"
                obs_str = v.observation if v.observation else "Sem observações."
                visits_data.append([date_str, Paragraph(obs_str, styles["NormalText"])])

        t_visits = Table(visits_data, colWidths=[30 * mm, 150 * mm])
        t_visits.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY_COLOR),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        Story.append(t_visits)

        # --- 7. Documentation ---
        Story.append(Paragraph("Auditoria Documental", styles["SectionTitle"]))
        docs_data = [["Documento Obrigatório", "Situação Atual"]]
        pending_docs = 0

        if not documents:
            docs_data.append(
                [Paragraph("Nenhum documento registrado.", styles["NormalText"]), ""]
            )
        else:
            for d in documents:
                status_real = d.status if d.status else "Pendente"
                if status_real == "Aprovado":
                    st_para = Paragraph(
                        f"<b><font color='#27AE60'>{status_real}</font></b>",
                        styles["NormalText"],
                    )
                else:
                    st_para = Paragraph(
                        f"<b><font color='#E67E22'>{status_real}</font></b>",
                        styles["NormalText"],
                    )
                    pending_docs += 1
                docs_data.append(
                    [Paragraph(d.document_name, styles["NormalText"]), st_para]
                )

        t_docs = Table(docs_data, colWidths=[130 * mm, 50 * mm])
        t_docs.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BG_LIGHT),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY_COLOR),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        Story.append(t_docs)
        Story.append(
            Paragraph(
                f"Total de pendências: <b>{pending_docs}</b>", styles["NormalText"]
            )
        )

        # --- 8. General Observations (Newly added section) ---
        Story.append(Paragraph("Observações Gerais", styles["SectionTitle"]))

        if not observations:
            Story.append(
                Paragraph("Nenhuma observação geral registrada.", styles["NormalText"])
            )
        else:
            obs_data = []
            for obs in observations:
                # Using getattr as a safety net in case the Observation schema differs
                date_str = getattr(obs, "date", getattr(obs, "created_at", "S/D"))
                text_str = getattr(
                    obs,
                    "text",
                    getattr(obs, "description", getattr(obs, "content", str(obs))),
                )

                obs_data.append(
                    [str(date_str), Paragraph(str(text_str), styles["NormalText"])]
                )

            t_obs = Table(obs_data, colWidths=[30 * mm, 150 * mm])
            t_obs.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                        ("PADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            Story.append(t_obs)

        # --- 9. Signatures (Using KeepTogether to prevent page breaks) ---
        date_emission = datetime.now().strftime("%d/%m/%Y às %H:%M")
        local_data_sig = (
            f"{city_state}, {datetime.now().strftime('%d de %B de %Y')}"
            if city_state
            else f"Emissão: {date_emission}"
        )

        sig_elements = [
            Spacer(1, 15 * mm),
            Paragraph(
                local_data_sig,
                ParagraphStyle("Center", parent=styles["NormalText"], alignment=1),
            ),
            Spacer(1, 20 * mm),
        ]

        # Signature lines
        linha_sup = Paragraph(
            f"<b>{supervisor_name}</b><br/>Supervisor(a) Acadêmico",
            ParagraphStyle("Center", parent=styles["NormalText"], alignment=1),
        )
        linha_int = Paragraph(
            f"<b>{intern.name}</b><br/>Discente",
            ParagraphStyle("Center", parent=styles["NormalText"], alignment=1),
        )

        t_sigs = Table(
            [[linha_sup, "", linha_int]], colWidths=[70 * mm, 20 * mm, 70 * mm]
        )
        t_sigs.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (0, 0), 1, colors.black),
                    ("LINEABOVE", (2, 0), (2, 0), 1, colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("PADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        sig_elements.append(t_sigs)

        sig_elements.append(Spacer(1, 10 * mm))
        sig_elements.append(
            Paragraph(
                f"Documento gerado eletronicamente em {date_emission} via Intern Manager Pro v1.2.0.<br/>Autenticidade sujeita a verificação.",
                styles["SmallText"],
            )
        )

        # KeepTogether forces the signature block to stay on the same page
        Story.append(KeepTogether(sig_elements))

        # --- Final Render ---
        doc.build(Story)
