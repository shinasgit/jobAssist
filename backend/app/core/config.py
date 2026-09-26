from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal Job Finder"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # SQLite configuration
    DATABASE_URL: str = "sqlite:///./job_assistant.db"

    class Config:
        env_file = ".env"

settings = Settings()
