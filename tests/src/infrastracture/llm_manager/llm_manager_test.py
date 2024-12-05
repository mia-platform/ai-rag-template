from langchain_openai import AzureChatOpenAI, ChatOpenAI
import pytest
from src.configurations.service_model import AzureLlmConfiguration, OpenAILlmConfiguration
from src.infrastracture.llm_manager.errors import UnsupportedLlmProviderError
from src.infrastracture.llm_manager.llm_manager import LlmManager


def test_get_llm_instance_from_default_configuration(app_context):
    llm_manager = LlmManager(app_context)
    llm_instance = llm_manager.get_llm_instance()

    assert llm_instance is not None
    assert isinstance(llm_instance, ChatOpenAI)


def test_get_llm_instance_from_openai_configuration(app_context):
    app_context.configurations.llm = OpenAILlmConfiguration(
        type="openai",
        name="text-llm-3-small"
    )

    llm_manager = LlmManager(app_context)
    llm_instance = llm_manager.get_llm_instance()

    assert llm_instance is not None
    assert isinstance(llm_instance, ChatOpenAI)


def test_get_llm_instance_from_azure_configuration(app_context):
    app_context.configurations.llm = AzureLlmConfiguration(
        apiVersion="2023-03-15-preview",
        deploymentName="dep-",
        name="text-llm-3-small",
        type="azure",
        url="https://example.azure.com",
    )

    llm_manager = LlmManager(app_context)
    llm_instance = llm_manager.get_llm_instance()

    assert llm_instance is not None
    assert isinstance(llm_instance, AzureChatOpenAI)

def test_fail_to_get_llm_instance_from_unsupported_configuration(app_context):
    app_context.configurations.llm = OpenAILlmConfiguration(
        type="unsupported",
        name="text-llm-3-small"
    )

    llm_manager = LlmManager(app_context)
    with pytest.raises(UnsupportedLlmProviderError):
        llm_manager.get_llm_instance()
