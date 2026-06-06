from pathlib import Path

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from app.config import REPORTS_DIR


class ReportService:

    def __init__(self):

        self.styles = getSampleStyleSheet()

    def generate_report(
        self,
        title: str,
        content: str,
        filename: str
    ):

        file_path = (
            REPORTS_DIR /
            filename
        )

        doc = SimpleDocTemplate(
            str(file_path)
        )

        elements = []

        title_paragraph = Paragraph(
            title,
            self.styles["Title"]
        )

        content_paragraph = Paragraph(
            content.replace("\n", "<br/>"),
            self.styles["BodyText"]
        )

        elements.append(title_paragraph)

        elements.append(
            Spacer(1, 20)
        )

        elements.append(content_paragraph)

        doc.build(elements)

        return str(file_path)