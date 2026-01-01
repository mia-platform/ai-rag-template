import os
from logging import Logger
from typing import Generic, TypeVar

from attr import dataclass
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

from src.infrastracture.env_vars_manager.errors import ModelValidationError

T = TypeVar("T", bound=BaseModel)


@dataclass
class EnvVarsParams:
    model: type[T]
    logger: Logger


class EnvVarsManager(Generic[T]):
    def __init__(self, params: EnvVarsParams):
        self.model = params.model
        self.logger = params.logger
        self.env_vars: T = os.environ

        self.env_vars = self.convert_to_pydantic()

    def convert_to_pydantic(self) -> T:
        """Convert the loaded env vars dictionary to a Pydantic model."""
        try:
            return self.model(**self.env_vars)
        except PydanticValidationError as err:
            self.logger.error(f"Pydantic model validation error: {err.errors()}")
            raise ModelValidationError(err.errors())

    def get_env_vars(self) -> T:
        return self.env_vars
