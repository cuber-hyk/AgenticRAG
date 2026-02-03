import logging
from typing import Any
from ..config import Settings
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.core.llms import CustomLLM, CompletionResponse, CompletionResponseGen, LLMMetadata
from llama_index.core import Settings as LlamaSettings
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


class SimpleLangChainAdapter(CustomLLM):
    _lc_model: Any = None

    def __init__(self, lc_model: Any):
        super().__init__()
        self._lc_model = lc_model

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata()

    def complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        try:
            msg = HumanMessage(content=prompt)
            out = self._lc_model.invoke([msg])
            return CompletionResponse(text=str(out.content))
        except Exception as e:
            logger.error(f"LangChain invoke error: {e}")
            raise e

    def stream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseGen:
        msg = HumanMessage(content=prompt)
        for chunk in self._lc_model.stream([msg]):
            yield CompletionResponse(text=str(chunk.content), delta=str(chunk.content))


class SiliconCloudLLM:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._adapter = None

        if self.settings.siliconcloud_api_key:
            try:
                # Initialize LangChain Chat Model (OpenAI compatible)
                # Note: config.py default base_url already includes /v1 if using default
                # But if user overrides it, we need to be careful.
                # Common practice: ensure it ends with /v1
                base_url = self.settings.siliconcloud_base_url
                if not base_url.endswith("/v1"):
                     base_url = f"{base_url}/v1"

                chat_model = init_chat_model(
                    model=self.settings.siliconcloud_model,
                    model_provider="openai",
                    api_key=self.settings.siliconcloud_api_key,
                    base_url=base_url,
                    temperature=0.2,
                    max_tokens=512,
                    timeout=self.settings.llm_timeout_seconds,
                )

                # Use our custom adapter which inherits from CustomLLM to provide default implementations
                self._adapter = SimpleLangChainAdapter(lc_model=chat_model)

                # Update global LlamaIndex settings
                LlamaSettings.llm = self._adapter

                # Initialize Embedding Model
                if self.settings.siliconcloud_embed_model:
                    embeddings_model = OpenAIEmbeddings(
                        model=self.settings.siliconcloud_embed_model,
                        openai_api_key=self.settings.siliconcloud_api_key,
                        openai_api_base=base_url,
                        check_embedding_ctx_length=False
                    )
                    LlamaSettings.embed_model = LangchainEmbedding(langchain_embeddings=embeddings_model)

            except Exception as e:
                logger.error(f"Failed to initialize SiliconCloud LLM: {e}")
                self._adapter = None

    def complete(self, prompt: str) -> str:
        if not self._adapter:
            return "【提示】未配置硅基流动API密钥或初始化失败，返回模拟回答：\n" + prompt[:200]
        try:
            response = self._adapter.complete(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"siliconcloud api error: {e}")
            return "LLM调用失败，已触发降级回答。"
