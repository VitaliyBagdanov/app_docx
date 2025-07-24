from fastapi import APIRouter, HTTPException, status
from .dao import MfgBotDAO
from .schemas import DocxV3Request, DocxV3Response
from ..docx_handler import generate_filled_docx, extract_tags_from_docx
from ..config import settings
import os
import tempfile


router = APIRouter()

@router.post(
     "/generate-docx",
    response_model=DocxV3Response,
    summary="Генерация DOCX",
    description="Генерирует .docx-файл по шаблону на основе данных из БД."
)
async def generate_docx_v3(request: DocxV3Request):
    """
    Генерация docx по шаблону:
    - Берет данные из БД по id и из request.values.
    - Возвращает статус, имя файла и детали.
    """
    template_path = os.path.join(settings.DOCX_SHARED_DIR, settings.DOCX_TEMPLATE_FILENAME)
    if not os.path.isfile(template_path):
        raise HTTPException(status_code=500, detail="Template file not found.")

    tags = extract_tags_from_docx(template_path)
    db_row = await MfgBotDAO.get_by_id(request.id)
    if not db_row:
        raise HTTPException(status_code=404, detail=f"Document with id {request.id} not found")

    fill_values = {tag: getattr(db_row, tag, None) for tag in tags}
    fill_values.update(request.values or {})
    # Валидация тегов (см. v2)
    missing_fields = [tag for tag in tags if tag not in fill_values]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(missing_fields)}")
    # Генерация docx
    output_filename = f"v3_{request.id}_output.docx"
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, output_filename)
    generate_filled_docx(template_path, output_path, fill_values)
    return DocxV3Response(status="success", filename=output_filename)
