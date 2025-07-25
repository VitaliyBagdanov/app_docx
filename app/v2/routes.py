from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from datetime import datetime
from .db_v2 import db_v2
from ..docx_handler import generate_filled_docx, extract_tags_from_docx
from ..config import settings
from .schemas import DocxV2Request
from .utils import format_russian_date
from .logger import logger
import os
import tempfile


router = APIRouter()


@router.post("/generate-docx")
async def generate_docx_v2(request: DocxV2Request):
    # 1. Определяем путь к шаблону
    logger.info(f"Start docx generation, doc_id={request.id}")
    template_path = os.path.join(settings.DOCX_SHARED_DIR, settings.DOCX_TEMPLATE_FILENAME)
    if not os.path.isfile(template_path):
        logger.error(f"Template file not found: {template_path}")
        raise HTTPException(
            status_code=500,
            detail="Template file not found in shared_data"
        )

    # 2. Извлекаем все теги для динамического запроса к БД
    tags = extract_tags_from_docx(template_path)

    # 3. Получаем значения этих полей из базы по id
    db_row = await db_v2.fetch_document_dynamic(request.id, tags)
    if not db_row:
        logger.error(f"Document with id {request.id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {request.id} not found"
        )

    # 4. Объединяем значения из БД и values из запроса (приоритет - values)
    fill_values = db_row.copy()
    fill_values.update(request.values or {})

    # 5. Проверяем наличие таблиц согласно тегов
    missing_fields = [tag for tag in tags if tag not in fill_values]
    if missing_fields:
        logger.error(f"В таблице нет следующих полей: {', '.join(missing_fields)}")
        raise HTTPException(
            status_code=400,
            detail=f"В таблице нет следующих полей: {', '.join(missing_fields)}"
        )
    
    # 6. Перевод даты в русском стиле
    for key, val in fill_values.items():
        if isinstance(val, (datetime, )):
            fill_values[key] = format_russian_date(val)
        elif isinstance(val, str):
            try:
                dt = datetime.fromisoformat(val)
                fill_values[key] = format_russian_date(dt)
            except Exception:
                pass

    # 7. Формируем временный файл
    output_filename = f"v2_{request.id}_output.docx"
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, output_filename)

    try:
        generate_filled_docx(template_path, output_path, fill_values)
        logger.info(f"Docx file generated: {output_path}")
    except Exception as e:
        logger.exception("Error generating docx")
        raise HTTPException(status_code=500, detail=f"Error generating docx: {e}")

    # 8. Отдаем файл с мета-информацией в заголовках
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
