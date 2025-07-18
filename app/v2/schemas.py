from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class DocxV2Request(BaseModel):
    id: int = Field(..., example=1)
    # Хранилище для любых других динамических шаблонных значений (str, int и т.п.)
    values: Dict[str, Any] = Field(default_factory=dict, description="Values for template tags")

class DocxV2Response(BaseModel):
    status: str = Field(..., example="success")
    filename: str = Field(..., example="output.docx")
    detail: Optional[str] = Field(None)
    # Сам файл возвращается в теле ответа, в схеме не нужен — будет через StreamingResponse/FileResponse
