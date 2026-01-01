from langchain_core.embeddings import Embeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

from src.context import AppContext
from src.infrastracture.embeddings_manager.errors import UnsupportedEmbeddingsProviderError


class EmbeddingsManager:
    def __init__(self, app_context: AppContext):
        self.app_context = app_context

    def get_embeddings_instance(self) -> Embeddings:
        embeddings_api_key = self.app_context.env_vars.EMBEDDINGS_API_KEY
        embeddings_configuration = self.app_context.configurations.embeddings

        match embeddings_configuration.type:
            case "openai":
                return OpenAIEmbeddings(openai_api_key=embeddings_api_key, model=embeddings_configuration.name)
            case "azure":
                return AzureOpenAIEmbeddings(
                    api_key=embeddings_api_key,
                    api_version=embeddings_configuration.apiVersion,
                    azure_deployment=embeddings_configuration.deploymentName,
                    azure_endpoint=embeddings_configuration.url,
                    model=embeddings_configuration.name,
                )
            case _:
                raise UnsupportedEmbeddingsProviderError(embeddings_configuration.type)
