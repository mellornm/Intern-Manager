import os
from datetime import datetime
from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout, QImage
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtCore import QMarginsF, QSettings, QByteArray, QBuffer, QIODevice

from core.models.intern import Intern
from core.models.grade import Grade
from core.models.evaluation_criteria import EvaluationCriteria
from core.models.venue import Venue
from core.models.document import Document
from core.models.meeting import Meeting
from core.models.observation import Observation


class ReportService:
    """
    Serviço de Geração de Relatórios (PDF).
    Gera um relatório completo usando dados do QSettings para personalização.
    """

    def _get_image_base64(self, path):
        """Lê a imagem do disco e converte para Base64 para embutir no HTML."""
        if not path or not os.path.exists(path):
            return ""

        image = QImage(path)
        if image.isNull():
            return ""

        # Redimensionar se for muito grande
        if image.height() > 120:
            image = image.scaledToHeight(120)

        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)

        image.save(buffer, "PNG")  # type: ignore

        return f"data:image/png;base64,{ba.toBase64().toStdString()}"

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
    ):
        # --- 1. Carregar Configurações ---
        settings = QSettings("MyOrganization", "InternManager2026")

        inst_name = settings.value("institution_name", "Instituição de Ensino")
        supervisor_name = settings.value("coordinator_name", "")
        city_state = settings.value("city_state", "")
        logo_path = settings.value("logo_path", "")

        # Processar Logo
        logo_html = ""
        if logo_path:
            b64 = self._get_image_base64(logo_path)
            if b64:
                logo_html = f'<img src="{b64}" class="logo-img">'

        # Cabeçalho Dinâmico
        header_subtext = ""
        if supervisor_name:
            header_subtext += f"Supervisor(a): {supervisor_name}<br>"

        # --- 2. Processamento de Dados ---

        # Notas
        grades_map = {
            g.criteria_id: g.value for g in grades if g.criteria_id is not None
        }
        total_score = 0.0
        max_score = 0.0

        grades_html_rows = ""
        for c in criteria_list:
            if c.criteria_id is None:
                continue
            val = grades_map.get(c.criteria_id, 0.0)
            total_score += val
            max_score += c.weight

            color = "#2E7D32" if val >= (c.weight * 0.7) else "#C62828"
            grades_html_rows += f"""
            <tr>
                <td>{c.name}</td>
                <td class="text-center">{c.weight:.1f}</td>
                <td class="text-center" style="color: {color}; font-weight: bold;">{val:.1f}</td>
            </tr>
            """

        status_text = "APROVADO" if total_score >= 7.0 else "EM ANÁLISE"
        status_color = "#2E7D32" if total_score >= 7.0 else "#C62828"

        # Frequência
        total_meetings = len(meetings)
        present_meetings = sum(1 for m in meetings if m.is_intern_present)
        freq_percent = (
            (present_meetings / total_meetings * 100) if total_meetings > 0 else 0.0
        )

        # Documentos
        docs_rows = ""
        pending_docs = 0
        for d in documents:
            # CORREÇÃO DE LÓGICA AQUI: Comparação explícita com "Aprovado"
            if d.status == "Aprovado":
                st = "<span style='color:#2E7D32; font-weight:bold'>Aprovado</span>"
            else:
                # Se for Pendente, Reprovado ou Vazio, cai aqui
                status_real = d.status if d.status else "Pendente"
                st = f"<span style='color:#C62828; font-weight:bold'>{status_real}</span>"
                pending_docs += 1

            docs_rows += (
                f"<tr><td>{d.document_name}</td><td class='text-center'>{st}</td></tr>"
            )

        # Observações
        obs_html = ""
        if observations:
            obs_html = "<ul>"
            for o in observations:
                data_obs = o.last_update if o.last_update else "S/D"
                obs_html += f"<li style='margin-bottom: 5px;'><b>[{data_obs}]:</b> {o.observation}</li>"
            obs_html += "</ul>"
        else:
            obs_html = "<p style='color:#777; margin-left: 10px;'><i>Nenhuma observação registrada.</i></p>"

        # Dados do Local
        if venue:
            venue_html = f"""
            <table class="info-table">
                <tr><th>Local:</th><td>{venue.venue_name}</td></tr>
                <tr><th>Supervisor Local:</th><td>{venue.supervisor_name or "-"}</td></tr>
                <tr><th>Contato:</th><td>{venue.supervisor_email or "-"} / {venue.supervisor_phone or "-"}</td></tr>
            </table>
            """
        else:
            venue_html = "<p style='color:red; font-style:italic;'>Local de estágio não vinculado.</p>"

        # Datas
        date_emission = datetime.now().strftime("%d/%m/%Y às %H:%M")

        start_fmt = intern.formatted_start_date
        end_fmt = intern.formatted_end_date

        local_data_sig = (
            f"{city_state}, {datetime.now().strftime('%d de %B de %Y')}"
            if city_state
            else f"Emissão: {date_emission}"
        )

        # --- 3. HTML Template ---
        html = f"""
        <html>
        <head>
        <meta charset="utf-8">
        <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10pt; color: #222; line-height: 1.4; }}
        .header {{ text-align: center; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }}
        .logo-img {{ height: 80px; margin-bottom: 8px; }}
        .header-title {{ font-size: 18pt; font-weight: bold; color: #003366; }}
        .header-sub {{ font-size: 9.5pt; color: #555; }}
        h2 {{ font-size: 12pt; color: #003366; border-bottom: 2px solid #003366; padding-bottom: 4px; margin-top: 18px; margin-bottom: 8px; text-transform: uppercase; }}
        .info-box {{ border: 1px solid #ddd; padding: 8px; margin-bottom: 10px; }}
        .info-table {{ width: 100%; border-collapse: collapse; }}
        .info-table th {{ text-align: left; width: 120px; font-weight: bold; padding: 4px 6px 4px 0; }}
        .info-table td {{ padding: 4px 0; }}
        .grid {{ width: 100%; border-collapse: collapse; font-size: 9pt; }}
        .grid th {{ background: #eaeaea; border: 1px solid #000; padding: 6px; text-align: left; }}
        .grid td {{ border: 1px solid #000; padding: 6px; }}
        .text-center {{ text-align: center; }}
        .two-col {{ width: 100%; }}
        .left {{ width: 48%; float: left; }}
        .right {{ width: 48%; float: right; }}
        .clear {{ clear: both; }}
        .summary {{ border: 2px solid #ccc; width: 220px; float: right; text-align: center; padding: 8px; margin-top: 10px; }}
        .final-grade {{ font-size: 20pt; font-weight: bold; color: {status_color}; }}
        .signature {{ text-align: center; margin-top: 40px; }}
        .signature-line {{ width: 350px; border-top: 1px solid #000; margin: 0 auto; }}
        .footer {{ margin-top: 30px; font-size: 8.5pt; text-align: center; color: #777; }}
        .page-break {{ page-break-before: always; }}
        </style>
        </head>

        <body>

        <div class="header">
            {logo_html}
            <div class="header-title">{inst_name}</div>
            <div class="header-sub">
                {header_subtext}<br>
                Sistema de Gerenciamento de Estágios
            </div>
        </div>

        <div class="two-col">
            <div class="left">
                <h2>Identificação do Aluno</h2>
                <div class="info-box">
                    <table class="info-table">
                        <tr><th>Nome:</th><td><b>{intern.name}</b></td></tr>
                        <tr><th>RA:</th><td>{intern.registration_number}</td></tr>
                        <tr><th>Semestre:</th><td>{intern.term}</td></tr>
                        <tr><th>Vigência:</th><td>{start_fmt} a {end_fmt}</td></tr>
                        <tr><th>Jornada:</th><td>{intern.working_days or "-"}</td></tr>
                        <tr><th>Horário:</th><td>{intern.working_hours or "-"}</td></tr>
                    </table>
                </div>
            </div>

            <div class="right">
                <h2>Local de Estágio</h2>
                <div class="info-box">
                    {venue_html}
                </div>
            </div>
        </div>

        <div class="clear"></div>

        <h2>Avaliação Acadêmica</h2>
        <table class="grid">
        <thead>
        <tr>
            <th>Critério Avaliativo</th>
            <th width="80" class="text-center">Peso</th>
            <th width="80" class="text-center">Nota</th>
        </tr>
        </thead>
        <tbody>
        {grades_html_rows}
        </tbody>
        </table>

        <div style="margin-top:10px;">
            <div class="summary">
                <div style="font-size:9pt;">MÉDIA FINAL</div>
                <div class="final-grade">{total_score:.1f}</div>
                <div style="font-weight:bold; color:{status_color};">{status_text}</div>
            </div>

            <h3>Frequência</h3>
            <p>De <b>{total_meetings}</b> reuniões supervisionadas, o aluno compareceu a <b>{present_meetings}</b>.</p>
            <p>Percentual de Presença: <b>{freq_percent:.1f}%</b></p>
        </div>

        <div class="page-break">
        <h2>Status Documental</h2>
        <p>Pendências atuais: <b>{pending_docs}</b> documento(s).</p>

        <table class="grid">
        <thead>
        <tr><th>Documento</th><th width="150" class="text-center">Situação</th></tr>
        </thead>
        <tbody>
        {docs_rows}
        </tbody>
        </table>
        </div>

        <h2>Observações do Supervisor</h2>
        {obs_html}

        <div class="signature">
            <p>{local_data_sig}</p>
            <div class="signature-line"></div>
            <p style="font-size:9pt;">Assinatura do Responsável</p>
        </div>

        <div class="footer">
        Relatório gerado eletronicamente em {date_emission} via Intern Manager 2026.
        </div>

        </body>
        </html>
        """

        # --- 4. Renderização ---
        doc = QTextDocument()
        doc.setHtml(html)

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filepath)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        margins = QMarginsF(15, 15, 15, 15)
        printer.setPageMargins(margins, QPageLayout.Unit.Millimeter)

        doc.print_(printer)
