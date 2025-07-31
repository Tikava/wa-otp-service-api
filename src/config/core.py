from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    
    super_admin_secret: str
    jwt_secret: str
    access_token_expire_minutes: int
    whatsapp_api_url: str
    whatsapp_api_version: str
    db_name: str
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    app_port: int

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    

settings = Settings()