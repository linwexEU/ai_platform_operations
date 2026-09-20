from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = find_dotenv("app/.env")
load_dotenv(env_file)


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=env_file)
    
    APP_NAME: str
    
    SECRET_KEY: str
    ALGORITHM: str
    
    ACCESS_COOKIE_NAME: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    
    REFRESH_COOKIE_NAME: str
    REFRESH_TOKEN_EXPIRES_MINUTES: int
    
    SESSION_COOKIE_SECURE: bool
    
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    REDIS_HOST: str
    REDIS_PORT: int
    
    @property
    def DATABASE_URL(self) -> str: 
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str: 
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    
settings = Settings()
