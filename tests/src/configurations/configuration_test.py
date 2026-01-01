from pathlib import Path

import pytest

from src.configurations.configuration import get_configuration
from src.infrastracture.config_manager.errors import ConfigValidationError


def generate_file_path(file_path: str):
    current_dir = Path(__file__).parent
    return current_dir / file_path


def get_test_configuration(path, logger):
    file_path = generate_file_path(path)
    return get_configuration(file_path, logger)


@pytest.mark.parametrize(
    "title, config_path",
    [
        ("with minimal configuration", "assets/correct_config.json"),
        ("with OpenAI configuration", "assets/openai_config.json"),
        ("with Azure OpenAI configuration", "assets/azure_config.json"),
    ],
)
# pylint: disable=unused-argument
def test_get_valid_configuration(title, config_path, logger):
    config = get_test_configuration(config_path, logger)
    assert config is not None


def test_fail_non_existing_configuration_file(logger):
    with pytest.raises(FileNotFoundError):
        get_test_configuration("not_existing_file.json", logger)


@pytest.mark.parametrize(
    "title, config_path",
    [
        ("empty config", "assets/empty_config.json"),
        ("missing llm", "assets/missing_llm_config.json"),
        ("unknown llm type", "assets/unknown_llm_type_config.json"),
        ("unknown_embedding_type", "assets/unknown_embedding_type_config.json"),
    ],
)
# pylint: disable=unused-argument
def test_fail_invalid_configuration(title, config_path, logger):
    with pytest.raises(ConfigValidationError):
        get_test_configuration(config_path, logger)
