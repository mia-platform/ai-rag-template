from pathlib import Path

import pytest
from pydantic import BaseModel

from src.infrastracture.config_manager.config_manager import (
    ConfigManager,
    ConfigManagerParams,
    ConfigValidationError,
    ModelValidationError,
)


class Employee(BaseModel):
    id: int
    name: str
    position: str


class WrongEmployee(BaseModel):
    zombieArmour: int
    resilience: str


def setup_config_manager(model, config_filename: str, schema_filename: str, logger) -> ConfigManager:
    """
    Helper function to set up ConfigManager with given parameters.

    :param model: The Pydantic model class to be used with ConfigManager.
    :param config_filename: Filename of the config file located in the 'assets' directory.
    :param schema_filename: Filename of the schema file located in the 'assets' directory.
    :param logger: Logger instance to be used by ConfigManager.
    :return: Configured instance of ConfigManager.
    """
    current_dir = Path(__file__).parent
    config_path = current_dir / "assets" / config_filename
    schema_path = current_dir / "assets" / schema_filename

    params = ConfigManagerParams(
        config_path=str(config_path), config_schema_path=str(schema_path), model=model, logger=logger
    )
    return ConfigManager[model](params)


class TestConfigManager:
    def test_get_config_values(self, logger):
        config_manager = setup_config_manager(Employee, "right_config.json", "config_schema.json", logger)

        config = config_manager.get_configuration()

        assert config.name == "John Doe"
        assert config.id == 12345
        assert config.position == "Software Engineer"

    def test_get_config_error_non_existing_config(self, logger):
        with pytest.raises(FileNotFoundError):
            setup_config_manager(Employee, "non_existent_config.json", "config_schema.json", logger)

    def test_get_config_error_non_existing_schema(self, logger):
        with pytest.raises(FileNotFoundError):
            setup_config_manager(Employee, "right_config.json", "non_existent_schema.json", logger)

    def test_get_config_error_invalid_config(self, logger):
        with pytest.raises(ConfigValidationError):
            setup_config_manager(Employee, "wrong_config.json", "config_schema.json", logger)

    def test_get_config_error_invalid_schema(self, logger):
        with pytest.raises(ModelValidationError):
            setup_config_manager(WrongEmployee, "right_config.json", "config_schema.json", logger)
