import io
from unittest.mock import patch
from zipfile import ZipFile

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
        ("pdf_file.pdf", b"%PDF-1.4 ...pdf content...", "application/pdf"),
        ("md_file.md", b"# Markdown Title\nSome markdown text.", "text/markdown"),
        ("txt_file.txt", b"Plain text content.", "text/plain"),
    ]
)
def test_generate_embeddings_from_file(test_client, file_name, file_content, content_type):
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_text") as mock_generate_from_text, \
        patch("src.application.embeddings.file_parser.FileParser.extract_documents_from_file") as mock_extract_documents_from_file:
        mock_extract_documents_from_file.return_value = ["Mock content"]

        file = (file_name, file_content, content_type)
        files = {"file": file}
        response = test_client.post("/embeddings/generateFromFile", files=files)
        
        assert response.status_code == 200
        assert response.json() == {"statusOk": True}
        mock_generate_from_text.assert_called_once_with("Mock content")


def test_generate_embeddings_from_zip_file(test_client):
    # Generate a zip file for test purposes
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as zipf:
        zipf.writestr('txt_file.txt', "This is a text file\n")
        zipf.writestr('pdf_file.md', "This is a markdown file\n")
    buffer.seek(0)

    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_text") as mock_generate_from_text, \
        patch("src.application.embeddings.file_parser.FileParser.extract_documents_from_file") as mock_extract_documents_from_file:

        mock_extract_documents_from_file.return_value = ["This is a text file", "This is a markdown file"]
        files = {"file": ("zip_file.zip", buffer, "application/zip")}
        response = test_client.post("/embeddings/generateFromFile", files=files)

        assert response.status_code == 200
        assert response.json() == {"statusOk": True}

        assert mock_extract_documents_from_file.call_count == 1
        assert mock_generate_from_text.call_count == 2

        mock_generate_from_text.assert_any_call("This is a text file")
        mock_generate_from_text.assert_any_call("This is a markdown file")


def test_fail_generate_embeddings_from_unsupported_file(test_client):
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_text") as mock_generate_from_text, \
        patch("src.application.embeddings.file_parser.FileParser.extract_documents_from_file") as mock_extract_documents_from_file:
        files = {"file": ("unsupported_file.wrong", b"Content of an unsupported file", "application/octet-stream")}
        response = test_client.post("/embeddings/generateFromFile", files=files)
        
        assert response.status_code == 400
        assert response.json() == {"detail": "Application does not support this file type (content type: application/octet-stream)."}
        mock_extract_documents_from_file.assert_not_called()
        mock_generate_from_text.assert_not_called()

@pytest.mark.parametrize(
    "file_name, content_type",
    [
        ("zip_file.zip", "application/zip"),
        ("tar_file.tar", "application/x-tar"),
        ("gz_file.gz", "application/gzip"),
    ]
)
def test_fail_for_bad_archive_file(test_client, file_name, content_type):
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate_from_text") as mock_generate_from_text:
        files = {"file": (file_name, b"This is not a valid archive file", content_type)}
        response = test_client.post("/embeddings/generateFromFile", files=files)
        
        assert response.status_code == 400
        assert response.json() == {"detail": "The file uploaded is not a valid archive file."}
        mock_generate_from_text.assert_not_called()

def test_fail_generate_embeddings_from_file_for_conflicts(test_client):
    router.lock = True  # Simulate a process already in progress
    response = test_client.post("/embeddings/generateFromFile", files={"file": ("test.txt", io.BytesIO(b"Plain text content."), "text/plain")})
    
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
