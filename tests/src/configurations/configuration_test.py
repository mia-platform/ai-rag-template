from pathlib import Path
import pytest

from src.infrastracture.config_manager.errors import ConfigValidationError
from src.configurations.configuration import get_configuration


def generate_file_path(file_path: str):
    current_dir = Path(__file__).parent
    return current_dir / file_path


def get_test_configuration(path, logger):
    file_path = generate_file_path(path)
    return get_configuration(file_path, logger)


CORRECT_CONFIG_PATH = 'assets/correct_config.json'
INCORRECT_CONFIG_PATH = 'assets/wrong_config.json'
UNEXISTING_CONFIG_PATH = 'zombie_config/asd.json'


@pytest.mark.parametrize(
    "test_id, config_path, expected_exception",
    [
        (
            "it should load correct configuration",
            CORRECT_CONFIG_PATH,
            None
        ),
        (
            "it should raise FileNotFoundError for non-existing path",
            UNEXISTING_CONFIG_PATH,
            FileNotFoundError
        ),
        (
            "it should raise ConfigValidationError if the configuration is not valid against the schema",
            INCORRECT_CONFIG_PATH,
            ConfigValidationError
        ),
    ],
)
def test_get_configuration(test_id, config_path, expected_exception, logger):
    # pylint: disable=unused-argument

    if expected_exception is None:
        config = get_test_configuration(config_path, logger)
        assert config is not None
    else:
        with pytest.raises(expected_exception):
            get_test_configuration(config_path, logger)
