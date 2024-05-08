class ConfigValidationError(Exception):
    """Exception raised for errors in the configuration validation against the schema."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ModelValidationError(Exception):
    """Exception raised for errors during the conversion of the configuration to a Pydantic model."""

    def __init__(self, errors: list):
        super().__init__("Model validation failed.")
        self.errors = errors
