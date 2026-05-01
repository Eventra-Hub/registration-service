from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    DB_NAME: str
    JWT_SECRET: str
    RABBITMQ_URL: str
    PORT: int
    SERVICE_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()