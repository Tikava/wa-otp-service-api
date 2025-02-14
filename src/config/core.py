from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    
    super_admin_secret: str
    jwt_secret: str
    access_token_expire_minutes: int
    whatsapp_api_url: str
    whatsapp_api_version: str
    database_username: str
    database_password: str
    database_host: str
    database_port: str
    database_name: str


    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    

settings = Settings()