from unittest.mock import patch

import pytest

from src.api.controllers.embeddings.embeddings_handler import router


def test_generate_embeddings_from_url_success(test_client):
    url = "http://example.com"
    data = {"url": url}
    
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_url") as mock_generate:
        response = test_client.post("/embeddings/generate", json=data)
        
        assert response.status_code == 200
        assert response.json() == {"statusOk": True}
        mock_generate.assert_called_once_with(url, None)

def test_generate_embeddings_from_url_conflict(test_client):
    url = "http://example.com"
    data = {"url": url}
    
    router.lock = True  # Simulate a process already in progress
    response = test_client.post("/embeddings/generate", json=data)
    
    assert response.status_code == 409
    assert response.json() == {"detail": "A process to generate embeddings is already in progress."}
    router.lock = False  # Reset lock for other tests

@pytest.mark.parametrize(
    "file_name, file_content, content_type",
    [
        ("test.zip", b"PK\x03\x04...zip content...", "application/zip"),
        ("test.pdf", b"%PDF-1.4 ...pdf content...", "application/pdf"),
        ("test.md", b"# Markdown Title\nSome markdown text.", "text/markdown"),
        ("test.txt", b"Plain text content.", "text/plain"),
    ]
)
def test_generate_embeddings_from_file(test_client, file_name, file_content, content_type):
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_file") as mock_generate:
        file = (file_name, file_content, content_type)
        files = {"file": file}
        response = test_client.post("/embeddings/generate", files=files)
        
        assert response.status_code == 200
        assert response.json() == {"statusOk": True}
        mock_generate.assert_called_once_with(file)


def test_fail_generate_embeddings_from_unsupported_file(test_client):
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_file") as mock_generate:
        files = {"file": ("unsupported_file.wrong", b"Content of an unsupported file", "application/octet-stream")}
        response = test_client.post("/embeddings/generate", files=files)
        
        assert response.status_code == 400
        assert response.json() == {"statusOk": True}
        mock_generate.assert_not_called()

def test_fail_generate_embeddings_from_file_for_conflicts(test_client):
    router.lock = True  # Simulate a process already in progress
    response = test_client.post("/embeddings/generate", files={"file": ("test.txt", b"Plain text content.", "text/plain")})
    
    assert response.status_code == 409
    assert response.json() == {"detail": "A process to generate embeddings is already in progress."}
    router.lock = False  # Reset lock for other tests

def test_embeddings_status_idle(test_client):
    router.lock = False  # Ensure no process is running
    response = test_client.get("/embeddings/status")
    
    assert response.status_code == 200
    assert response.json() == {"status": "idle"}

def test_embeddings_status_running(test_client):
    router.lock = True  # Simulate a process running
    response = test_client.get("/embeddings/status")
    
    assert response.status_code == 200
    assert response.json() == {"status": "running"}
    router.lock = False  # Reset lock for other tests
