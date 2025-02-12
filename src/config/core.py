from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    
    whatsapp_api_url: str
    whatsapp_api_version: str
    db_user: str
    db_pass: str
    db_host: str
    db_name: str


    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    

settings = Settings()