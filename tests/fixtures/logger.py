import pytest

from src.infrastracture.logger import get_logger


@pytest.fixture(name="logger")
def fixture_logger():
    logger = get_logger()
    yield logger
