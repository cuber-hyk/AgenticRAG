import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    environment: str = Field(default="development")
    cors_allow_origins: List[str] = Field(default=["*"])

    weaviate_url: str = Field(default=os.getenv("WEAVIATE_URL", "http://localhost:8080"))
    weaviate_api_key: str = Field(default=os.getenv("WEAVIATE_API_KEY", ""))
    weaviate_class: str = Field(default=os.getenv("WEAVIATE_CLASS", "Documents"))

    siliconcloud_api_key: str = Field(default=os.getenv("SILICONCLOUD_API_KEY", ""))
    siliconcloud_base_url: str = Field(default=os.getenv("SILICONCLOUD_BASE_URL", "https://api.siliconflow.cn/v1"))
    siliconcloud_model: str = Field(default=os.getenv("SILICONCLOUD_MODEL", "Qwen/Qwen2.5-14B-Instruct"))
    siliconcloud_embed_model: str = Field(default=os.getenv("SILICONCLOUD_EMBED_MODEL", "Qwen/Qwen3-Embedding-8B"))
    llm_timeout_seconds: int = Field(default=60)  # 增加超时时间以避免ReadTimeout

    retrieval_top_k: int = Field(default=4)
    max_context_tokens: int = Field(default=4096)

    enable_streaming: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    class Config:
        env_file = ".env"
        extra = "ignore"
