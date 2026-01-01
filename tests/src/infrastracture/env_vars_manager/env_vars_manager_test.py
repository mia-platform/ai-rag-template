from pathlib import Path

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel

from src.infrastracture.env_vars_manager.env_vars_manager import EnvVarsManager, EnvVarsParams
from src.infrastracture.env_vars_manager.errors import ModelValidationError


def load_env_vars(file_name):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / file_name
    load_dotenv(file_path, override=True)


class RightEnvVars(BaseModel):
    THE_NUMBER: int
    ERROR_MESSAGE: str
    SECRET_SAUCE_INGREDIENT: str


class WrongEnvVars(BaseModel):
    logLevel: str
    port: int


def setup_env_vars_manager(model, logger) -> EnvVarsManager:
    params = EnvVarsParams(model=model, logger=logger)

    return EnvVarsManager[model](params)


class TestEnvVarsManager:
    def test_get_env_vars(self, logger):
        load_env_vars("test.env")

        env_vars_manager = setup_env_vars_manager(RightEnvVars, logger)

        env_vars = env_vars_manager.get_env_vars()

        assert env_vars.THE_NUMBER == 42
        assert env_vars.ERROR_MESSAGE == "I'm a teapot"
        assert env_vars.SECRET_SAUCE_INGREDIENT == "coffee"

    def test_get_env_vars_error_invalid_schema(self, logger):
        with pytest.raises(ModelValidationError):
            setup_env_vars_manager(WrongEnvVars, logger)
