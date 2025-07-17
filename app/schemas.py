from pydantic import BaseModel, Field

class DocxRequest(BaseModel):
    id: str = Field(..., example="math-001", min_length=1)

class DocxResponse(BaseModel):
    status: str = Field(..., example="success")
    filename: str = Field(..., example="math-001_output.docx")
    detail: str = Field(None, example="File generated and saved.")
