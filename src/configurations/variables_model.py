from pydantic import BaseModel, Field


class Variables(BaseModel):
    PORT: int | None = Field(3000, description="The port on which the application will run.")
    LOG_LEVEL: str | None = Field(
        "DEBUG",
        description="The logging level for the application.",
        json_schema_extra={"enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
    )
    CONFIGURATION_PATH: str | None = Field(
        "/app/configurations/config.json", description="The path to the configuration file for the application."
    )
    MONGODB_CLUSTER_URI: str = Field(description="The URI for connecting to the MongoDB cluster.")
    LLM_API_KEY: str = Field(description="The API key for accessing the Language Model API.")
    EMBEDDINGS_API_KEY: str = Field(description="The API key for accessing the Embeddings API.")
    HEADERS_TO_PROXY: str | None = Field(
        None, description="The headers to proxy from the client to the server during intra-service communication."
    )
