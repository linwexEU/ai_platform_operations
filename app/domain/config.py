from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file = find_dotenv("app/.env")
load_dotenv(env_file)


class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=env_file)
    
    APP_NAME: str
    
    SECRET_KEY: str
    ALGORITHM: str
    
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    REFRESH_TOKEN_EXPIRES_MINUTES: int
    ACCESS_COOKIE_NAME: str
    REFRESH_COOKIE_NAME: str
    
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    @property
    def DATABASE_URL(self) -> str: 
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    
settings = Settings()
