from pathlib import Path
from src.infrastracture.config_manager.config_manager import ConfigManager, ConfigManagerParams
from src.configurations.service_model import RagTemplateConfigSchema


CONFIG_SCHEMA_FILE_NAME = "service_config.json"

current_dir = Path(__file__).parent
schema_path = current_dir / CONFIG_SCHEMA_FILE_NAME


def get_configuration(config_path, logger):
    params = ConfigManagerParams(
        config_path=config_path,
        config_schema_path=schema_path,
        model=RagTemplateConfigSchema,
        logger=logger
    )

    conf_manager = ConfigManager[RagTemplateConfigSchema](params)

    return conf_manager.get_configuration()
