from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "LeadAggregator"
    APP_ENV: str = "development"
    SECRET_TOKEN: str = "mysecret123"
    DATABASE_URL: str = "sqlite:///./leads.db"
    LEAD_EXPIRY_DAYS: int = 30
    SCHEDULER_INTERVAL_MINUTES: int = 60
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""

    class Config:
        env_file = ".env"


settings = Settings()