from typing import Optional
from pydantic import BaseModel, Field


class Variables(BaseModel):
    PORT: Optional[int] = Field(
        3000,
        description='The port on which the application will run.'
    )
    LOG_LEVEL: Optional[str] = Field(
        'DEBUG',
        description='The logging level for the application.',
        json_schema_extra={
            "enum": ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        }
    )
    CONFIGURATION_PATH: Optional[str] = Field(
        '/app/configurations/config.json',
        description='The path to the configuration file for the application.'
    )
    MONGODB_CLUSTER_URI: str = Field(
        description='The URI for connecting to the MongoDB cluster.'
    )
    LLM_API_KEY: str = Field(
        description='The API key for accessing the Language Model API.'
    )
    EMBEDDINGS_API_KEY: str = Field(
        description='The API key for accessing the Embeddings API.'
    )
    HEADERS_TO_PROXY: Optional[str] = Field(
        None,
        description='The headers to proxy from the client to the server during intra-service communication.'
    )
