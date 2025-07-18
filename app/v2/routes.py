from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import FileResponse
from ..db import db
from ..docx_handler import generate_filled_docx
from ..config import settings
from .schemas import DocxV2Request
import os
import tempfile

router = APIRouter()

@router.post("/generate-docx")
async def generate_docx_v2(request: DocxV2Request):
    # 1. Получить данные из БД по id (если id не нужен — этот шаг убрать)
    db_row = await db.fetch_document(request.id)
    if not db_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with id {request.id} not found")

    # 2. Объединить значения: сначала из БД, поверх — из запроса
    # (в values могут быть любые override-поля)
    fill_values = db_row.copy()
    fill_values.update(request.values or {})

    # 3. Проверить наличие шаблона
    template_path = os.path.join(settings.DOCX_SHARED_DIR, "template.docx")
    if not os.path.isfile(template_path):
        raise HTTPException(status_code=500, detail="Template file not found in shared_data")

    # 4. Сгенерировать временный файл (или в shared_data, если нужно)
    output_filename = f"v2_{request.id}_output.docx"
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, output_filename)

    try:
        generate_filled_docx(template_path, output_path, fill_values)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating docx: {e}")

    # 5. Вернуть файл как attachment + мета
    headers = {
        "X-Status": "success",
        "X-Filename": output_filename,
        "X-Detail": "File generated and attached in response."
    }
    return FileResponse(
        output_path,
        filename=output_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )