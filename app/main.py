from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from .v2.routes import router as v2_router
from .schemas import DocxRequest, DocxResponse
from .db import db
from .docx_handler import generate_filled_docx
from .config import settings
import os

app = FastAPI(
    title="Docx Template Generation API",
    description="Генерация docx-файлов по шаблону и данным из Postgres.",
    version="1.0"
)

app.include_router(v2_router, prefix="/v2", tags=["v2"])

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.post("/generate-docx", response_model=DocxResponse)
async def generate_docx(request: DocxRequest):
    # 1. Поиск документа в базе
    doc_row = await db.fetch_document(request.id)
    if not doc_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {request.id} not found"
        )

    # 2. Проверка наличия шаблона
    template_path = os.path.join(settings.DOCX_SHARED_DIR, settings.DOCX_TEMPLATE_FILENAME)
    if not os.path.isfile(template_path):
        raise HTTPException(
            status_code=500,
            detail="Template file not found in shared_data"
        )

    # 3. Генерация файла
    output_filename = f"{request.id}_output.docx"
    output_path = os.path.join(settings.DOCX_SHARED_DIR, output_filename)
    try:
        generate_filled_docx(
            template_path=template_path,
            output_path=output_path,
            values=doc_row
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating docx: {e}"
        )

    # 4. Ответ клиенту
    return DocxResponse(
        status="success",
        filename=output_filename,
        detail="File generated and saved in shared_data."
    )
