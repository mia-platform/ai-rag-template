from src.configurations.variables_model import Variables
from src.infrastracture.env_vars_manager.env_vars_manager import EnvVarsManager, EnvVarsParams


def get_variables(logger):
    params = EnvVarsParams(Variables, logger)

    env_vars = EnvVarsManager[Variables](params)

    return env_vars.get_env_vars()
