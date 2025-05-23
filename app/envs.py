from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str
    HOST: str
    PORT: int

    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str

    ELEVENLABS_API_KEY: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')