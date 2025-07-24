from fastapi import FastAPI
from .v2.routes import router as v2_router
from .v2.logger import logger
from .v2.db_v2 import db_v2


app = FastAPI(
    title="Docx Template Generation API",
    description="Генерация docx-файлов по шаблону и данным из Postgres.",
    version="1.0"
)

app.include_router(v2_router, prefix="/v2", tags=["v2"])

@app.on_event("startup")
async def startup():
    await db_v2.connect()
    logger.info("Starting application...")

@app.on_event("shutdown")
async def shutdown():
    await db_v2.disconnect()
    logger.info("Shutting down...")
