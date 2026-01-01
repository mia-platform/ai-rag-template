import pytest
from fastapi.testclient import TestClient

from src.app import create_app


@pytest.fixture
def test_client(app_context):
    """
    This client can call the developed application
    """
    app = create_app(app_context)

    with TestClient(app) as client:
        return client
