from pathlib import Path
from unittest.mock import patch

from langchain_core.documents import Document

from src.application.assistance.service import AssistantServiceChatCompletionResponse


def read_txt(file_name):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / file_name

    with open(file_path, encoding="utf-8") as opened_file:
        return opened_file.read()


@patch(
    "src.application.assistance.service.AssistantService.chat_completion",
)
def test_chat_completions(chat_completion_mock, test_client):
    # Arrange
    completion_mock_response = AssistantServiceChatCompletionResponse(
        response="Mocked response",
        references=[
            Document(page_content="doc1", metadata={"url": "www.mia-platform.eu"}),
            Document(page_content="doc2", metadata={"url": None}),
            Document(page_content="doc3", metadata={}),
        ],
    )
    chat_completion_mock.return_value = completion_mock_response

    request_data = {"chat_query": "Test query", "chat_history": ["History 1", "History 2"]}

    # Act
    response = test_client.post("/chat/completions", json=request_data)

    # Assert
    expected = {
        "message": completion_mock_response.response,
        "references": [
            {"content": "doc1", "url": "www.mia-platform.eu"},
            {"content": "doc2", "url": None},
            {"content": "doc3", "url": None},
        ],
    }

    response_data = response.json()

    assert response.status_code == 200
    assert response_data["message"] == expected["message"]
    assert response_data["references"] == expected["references"]

    chat_completion_mock.assert_called_once_with(
        query=request_data["chat_query"], chat_history=request_data["chat_history"]
    )


def test_chat_completions_chat_query_validation(test_client):
    # Arrange
    request_data = {"chat_query": read_txt("long_text.txt"), "chat_history": ["History 1", "History 2"]}

    # Act
    response = test_client.post("/chat/completions", json=request_data)

    error = response.json()

    # Assert
    assert response.status_code == 413
    assert error["detail"] == "chat_query length exceeds 2000 characters"


def test_chat_completions_chat_history_validation(test_client):
    # Arrange
    request_data = {"chat_query": "Test query", "chat_history": ["History 1"]}

    # Act
    response = test_client.post("/chat/completions", json=request_data)

    error = response.json()

    # Assert
    assert response.status_code == 422
    assert error["detail"][0]["msg"] == "Value error, chat_history length must be even"
