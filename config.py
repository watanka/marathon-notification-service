from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import model_validator

class Settings(BaseSettings):
    # Database 설정
    DEPLOY_ENV: str = 'local'
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "superuser"
    DB_PASSWORD: str
    DB_NAME: str = "marathon_db"
    SQLALCHEMY_DATABASE_URL: str | None = None

    # Twilio 설정
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str
    
    # Telegram 설정
    TELEGRAM_BOT_TOKEN: str

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    
    @model_validator(mode='after')
    def set_database_url(self) -> 'Settings':
        self.SQLALCHEMY_DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()