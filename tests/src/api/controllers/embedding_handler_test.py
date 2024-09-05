from unittest.mock import patch

from src.api.controllers.embeddings.embeddings_handler import router


def test_generate_embeddings_success(test_client):
    url = "http://example.com"
    data = {"url": url}
    
    with patch("src.api.controllers.embeddings.embeddings_handler.EmbeddingGenerator.generate") as mock_generate:
        response = test_client.post("/embeddings/generate", json=data)
        
        assert response.status_code == 200
        assert response.json() == {"statusOk": True}
        mock_generate.assert_called_once_with(url)

def test_generate_embeddings_conflict(test_client):
    url = "http://example.com"
    data = {"url": url}
    
    router.lock = True  # Simulate a process already in progress
    response = test_client.post("/embeddings/generate", json=data)
    
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
