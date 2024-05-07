from pathlib import Path
from dotenv import load_dotenv

from src.configurations.variables import get_variables


def load_env_vars(file_name):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / file_name
    load_dotenv(file_path, override=True)


def test_get_variables(logger):
    load_env_vars("test.env")

    env_vars = get_variables(logger)

    assert env_vars.PORT == 3000
    assert env_vars.LOG_LEVEL == "WARNING"
    assert env_vars.CONFIGURATION_PATH == "/my/configuration/path"
