from langchain_openai import AzureChatOpenAI
from envs import Settings

settings = Settings()

llm = AzureChatOpenAI(
    azure_deployment="gpt-35-turbo",
    api_version="2024-08-01-preview",
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY
)