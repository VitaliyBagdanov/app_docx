from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_DB: str 
    POSTGRES_HOST: str 
    POSTGRES_PORT: str 
    DOCX_SHARED_DIR: str 

settings = Settings()
