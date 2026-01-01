from fastapi import APIRouter, FastAPI, Request
from fastapi.testclient import TestClient

from src.api.middlewares.logger_middleware import LoggerMiddleware
from src.infrastracture.logger import get_logger

router = APIRouter()


@router.get("/")
def read_root(request: Request):
    request.state.logger.info("Root path called")
    return {"Hello": "World"}


def setup_test_app():
    app = FastAPI()
    logger = get_logger()
    app.add_middleware(LoggerMiddleware, logger=logger)
    app.include_router(router)
    client = TestClient(app)
    return client


def test_logger_middleware_req_id(capfd):
    # Arrange
    client = setup_test_app()

    # Act
    response = client.get("/", headers={"x-request-id": "1234"})

    # Assert
    assert response.status_code == 200
    captured = capfd.readouterr()
    assert '"reqId": "1234"' in captured.out
