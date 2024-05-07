import json
from unittest.mock import patch
from pathlib import Path
import pytest
from httpx import Response
from langchain_core.documents import Document

from src.configurations.service_model import PromptsFilePath, Rag
from src.application.assistance.chains.assistant_prompt import AssistantPromptBuilder
from src.application.assistance.service import AssistantService, AssistantServiceConfiguration


def load_json_response(file_name):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / file_name

    with open(file_path, "r", encoding="utf-8") as opened_file:
        return json.loads(opened_file.read())


def test_init(app_context):
    try:
        instance = AssistantService(
            app_context=app_context
        )
        assert isinstance(instance, AssistantService)
    # pylint: disable=broad-except
    except Exception:
        pytest.fail("Creating instance of AssistantService failed")

def test_init_with_db_name_from_uri(app_context):
    try:
        modified_app_context = app_context
        modified_app_context.configurations.vectorStore.dbName = None
        modified_app_context.env_vars.MONGODB_CLUSTER_URI = "mongodb://localhost:27017/db_name"
        
        instance = AssistantService(
            app_context=app_context
        )
        assert isinstance(instance, AssistantService)
    # pylint: disable=broad-except
    except Exception:
        pytest.fail("Creating instance of AssistantService failed")

@patch(
    'langchain_mongodb.MongoDBAtlasVectorSearch._similarity_search_with_score',
)
def test_chat_completion(
    similarity_search_with_score,
    app_context,
    mock_server,
    snapshot
):
    # Arrange
    assistant_service = AssistantService(
        app_context=app_context
    )

    similarity_search_with_score.return_value = [
        (
            Document(
                page_content="doc1",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
        (
            Document(
                page_content="doc2",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
        (
            Document(
                page_content="doc3",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
    ]

    embedding_reply_mock = load_json_response("openai_embedding.json")
    chat_completion_reply_mock = load_json_response(
        "openai_chat_completion.json")

    mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/embeddings")\
        .mock(return_value=Response(
            200,
            json=embedding_reply_mock))

    chat_completion = mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/chat/completions")\
        .mock(return_value=Response(
            200,
            json=chat_completion_reply_mock))

    # Act
    result = assistant_service.chat_completion(
        query="query",
        chat_history=[
            "Chat message 1",
            "Chat message 2",
            "Chat message 3",
            "Chat message 4"
        ]
    )

    # Assert

    snapshot.assert_match(
        chat_completion.calls[0][0].content, "chat_completion_request")
    
    assert result.response == chat_completion_reply_mock['choices'][0]['message']['content']

@patch(
    'langchain_mongodb.MongoDBAtlasVectorSearch._similarity_search_with_score',
)
def test_chat_completion_with_custom_template(
    similarity_search_with_score,
    app_context,
    mock_server,
    snapshot
):
    # Arrange
    assistant_service_config = AssistantServiceConfiguration(
        prompt_template= AssistantPromptBuilder()
            .append_to_system_template("This is a custom template addition with a variable: {a_custom_variable}")
            .add_variable("a_custom_variable")
            .build()
    )
    
    assistant_service = AssistantService(
        app_context=app_context,
        configuration=assistant_service_config
    )

    similarity_search_with_score.return_value = [
        (
            Document(
                page_content="doc1",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
        (
            Document(
                page_content="doc2",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
        (
            Document(
                page_content="doc3",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
    ]

    embedding_reply_mock = load_json_response("openai_embedding.json")
    chat_completion_reply_mock = load_json_response(
        "openai_chat_completion.json")

    mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/embeddings")\
        .mock(return_value=Response(
            200,
            json=embedding_reply_mock))

    chat_completion = mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/chat/completions")\
        .mock(return_value=Response(
            200,
            json=chat_completion_reply_mock))

    # Act
    result = assistant_service.chat_completion(
        query="query",
        chat_history=[
            "A long chat history..."
        ],
        custom_template_variables={"a_custom_variable": "a_custom_variable_value"}
    )

    # Assert

    snapshot.assert_match(
        chat_completion.calls[0][0].content, "chat_completion_request")
    
    assert result.response == chat_completion_reply_mock['choices'][0]['message']['content']

@patch(
    'langchain_mongodb.MongoDBAtlasVectorSearch._similarity_search_with_score',
)
def test_chat_completion_with_prompts_from_file(
    similarity_search_with_score,
    app_context,
    mock_server,
    snapshot,
    tmp_path
):
    # Create prompt template files
    system_template = "{output_text} {chat_history} {custom_variable} you MUST reply to Human question"
    user_template = "{query}"
    system_template_file = tmp_path / "system_template.txt"
    user_template_file = tmp_path / "user_template.txt"
    with open(system_template_file, 'w', encoding="utf-8") as file:
        file.write(system_template)
        
    with open(user_template_file, 'w', encoding="utf-8") as file:
        file.write(user_template)
    
    # Patch configuration to use prompt templates from file
    app_context.configurations.chain.rag = Rag(
        promptsFilePath= PromptsFilePath(
            system=str(system_template_file.absolute()),
            user=str(user_template_file.absolute())
        )
    ) 
    
    # Arrange
    assistant_service = AssistantService(
        app_context=app_context
    )

    similarity_search_with_score.return_value = [
        (
            Document(
                page_content="doc1",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
        (
            Document(
                page_content="doc2",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
        (
            Document(
                page_content="doc3",
                metadata={"url": "www.mia-platform.eu"}
            ),
            0.5
        ),
    ]

    embedding_reply_mock = load_json_response("openai_embedding.json")
    chat_completion_reply_mock = load_json_response(
        "openai_chat_completion.json")

    mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/embeddings")\
        .mock(return_value=Response(
            200,
            json=embedding_reply_mock))

    chat_completion = mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/chat/completions")\
        .mock(return_value=Response(
            200,
            json=chat_completion_reply_mock))

    # Act
    result = assistant_service.chat_completion(
        query="query",
        chat_history=[
            "A long chat history..."
        ],
        custom_template_variables={"custom_variable": "custom_variable_value"}
    )

    # Assert

    snapshot.assert_match(
        chat_completion.calls[0][0].content, "chat_completion_request_with_prompts_from_file")
    
    assert result.response == chat_completion_reply_mock['choices'][0]['message']['content']
