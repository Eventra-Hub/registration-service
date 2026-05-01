from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URL: str
    DB_NAME: str
    JWT_SECRET: str
    RABBITMQ_URL: str
    PORT: int = 8000
    SERVICE_NAME: str = "registration-service"
    EVENT_SERVICE_URL: str = "http://event-service:8000"
    USER_SERVICE_URL: str = "http://user-service:8000"

    class Config:
        env_file = ".env"

settings = Settings()
