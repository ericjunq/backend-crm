from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str 
    database_url: str 
    access_token_expires_minutes: int 
    refresh_token_expires_days: int 
    algorithm: str 
    database_url_test: str

    class Config:
        env_file = '.env'

settings = Settings()