from docx import Document
import os

def generate_filled_docx(template_path: str, output_path: str, values: dict):
    """
    Заменяет {secretary}, {body} в документе и сохраняет в output_path
    """
    doc = Document(template_path)

    # Заменяем плейсхолдеры во всех параграфах
    for paragraph in doc.paragraphs:
        for key, val in values.items():
            if f"{{{key}}}" in paragraph.text:
                paragraph.text = paragraph.text.replace(f"{{{key}}}", str(val))

    # Заменяем в таблицах (если вдруг плейсхолдеры там)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, val in values.items():
                    if f"{{{key}}}" in cell.text:
                        cell.text = cell.text.replace(f"{{{key}}}", str(val))

    doc.save(output_path)
