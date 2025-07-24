from pydantic_settings import BaseSettings
from dotenv import load_dotenv; load_dotenv()


class Settings(BaseSettings):
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_DB: str 
    POSTGRES_HOST: str 
    POSTGRES_PORT: str 
    DOCX_SHARED_DIR: str 
    DOCX_TEMPLATE_FILENAME: str = "template.docx"

settings = Settings()
