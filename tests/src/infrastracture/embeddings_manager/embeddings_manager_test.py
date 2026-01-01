import pytest
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from pydantic import ValidationError

from src.configurations.service_model import AzureEmbeddingsConfiguration, OpenAIEmbeddingsConfiguration
from src.infrastracture.embeddings_manager.embeddings_manager import EmbeddingsManager
from src.infrastracture.embeddings_manager.errors import UnsupportedEmbeddingsProviderError


def test_get_embeddings_instance_from_default_configuration(app_context):
    embeddings_manager = EmbeddingsManager(app_context)
    embeddings_instance = embeddings_manager.get_embeddings_instance()

    assert embeddings_instance is not None
    assert isinstance(embeddings_instance, OpenAIEmbeddings)


def test_get_embeddings_instance_from_openai_configuration(app_context):
    app_context.configurations.embeddings = OpenAIEmbeddingsConfiguration(type="openai", name="text-embeddings-3-small")

    embeddings_manager = EmbeddingsManager(app_context)
    embeddings_instance = embeddings_manager.get_embeddings_instance()

    assert embeddings_instance is not None
    assert isinstance(embeddings_instance, OpenAIEmbeddings)


def test_get_embeddings_instance_from_azure_configuration(app_context):
    app_context.configurations.embeddings = AzureEmbeddingsConfiguration(
        apiVersion="2023-03-15-preview",
        deploymentName="dep-",
        name="text-embeddings-3-small",
        type="azure",
        url="https://example.azure.com",
    )

    embeddings_manager = EmbeddingsManager(app_context)
    embeddings_instance = embeddings_manager.get_embeddings_instance()

    assert embeddings_instance is not None
    assert isinstance(embeddings_instance, AzureOpenAIEmbeddings)


def test_fail_to_get_embeddings_instance_from_unsupported_configuration(app_context):
    with pytest.raises(ValidationError):
        OpenAIEmbeddingsConfiguration(type="unsupported", name="text-embeddings-3-small")
