import httpx
import ssl
from langchain_openai import ChatOpenAI
from config import get_settings

settings = get_settings()

# SSL-disabled HTTP client for TCS internal proxy
_http_client = httpx.Client(verify=False)
_async_http_client = httpx.AsyncClient(verify=False)


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        temperature=temperature,
        http_client=_http_client,
        http_async_client=_async_http_client,
    )
