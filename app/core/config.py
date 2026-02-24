from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ecommerce"
    JWT_SECRET: str = "change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30    
    STRIPE_SECRET_KEY: str = ""
    MULTICARD_APP_ID: str = ""
    MULTICARD_SECRET: str = ""
    MULTICARD_TEST_MODE: bool = True

    class Config:
        env_file = ".env"

settings = Settings()