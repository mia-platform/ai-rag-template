from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from src.context import AppContext
from src.infrastracture.llm_manager.errors import UnsupportedLlmProviderError


class LlmManager:
    def __init__(self, app_context: AppContext):
        self.app_context = app_context

    def get_llm_instance(self) -> BaseChatModel:
        llm_api_key = self.app_context.env_vars.LLM_API_KEY
        llm_configuration = self.app_context.configurations.llm

        match llm_configuration.type:
            case "openai":
                return ChatOpenAI(openai_api_key=llm_api_key, model=llm_configuration.name, temperature=llm_configuration.temperature)
            case "azure":
                return AzureChatOpenAI(
                    api_key=llm_api_key,
                    api_version=llm_configuration.apiVersion,
                    azure_deployment=llm_configuration.deploymentName,
                    azure_endpoint=llm_configuration.url,
                    model=llm_configuration.name,
                    temperature=llm_configuration.temperature,
                )
            case _:
                raise UnsupportedLlmProviderError(llm_configuration.type)
