from typing import Literal

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = find_dotenv("app/.env")
load_dotenv(env_file)


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=env_file)
    
    MODE: Literal["DEV", "TEST"]
    
    APP_NAME: str
    
    SECRET_KEY: str
    ALGORITHM: str
    
    ACCESS_COOKIE_NAME: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    
    REFRESH_COOKIE_NAME: str
    REFRESH_TOKEN_EXPIRES_MINUTES: int
    
    VERIFICATION_CODE_MINUTES: int
    
    SESSION_COOKIE_SECURE: bool
    
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_NAME: str
    
    REDIS_HOST: str
    REDIS_PORT: int
    
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    
    AWS_ACCESS_KEY: str
    AWS_ACCESS_SECRET_KEY: str
    AWS_REGION_NAME: str
    AWS_BUCKET_NAME: str
    
    OLLAMA_CHAT_MODEL: str
    OLLAMA_EMBEDDING_MODEL: str
    EMBEDDING_DIMENSION: int
    EMBEDDING_BATCH: int
    
    VERIFICATION_CODE_TEMPLATE_PATH: str
    TEMP_FOLDER_PATH: str
    
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    CHUNKING_VERSION: int
    
    MAX_CONCURRENT: int
        
    @property
    def DATABASE_URL(self) -> str: 
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def TEST_DATABASE_URL(self) -> str: 
        return f"postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str: 
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def AWS_CREDENTIALS(self) -> dict[str, str]: 
        return {
            "aws_access_key_id": self.AWS_ACCESS_KEY,
            "aws_secret_access_key": self.AWS_ACCESS_SECRET_KEY, 
            "region_name": self.AWS_REGION_NAME
        }
    
    
settings = Settings()
