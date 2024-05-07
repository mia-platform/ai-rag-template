from unittest.mock import MagicMock
import pytest

from src.configurations.variables_model import Variables
from src.configurations.service_model import RagTemplateConfigSchema
from src.context import AppContext, AppContextParams


@pytest.fixture
def app_context():

    mock_env_vars = Variables(
        PORT="3000",
        LOG_LEVEL="DEBUG",
        CONFIGURATION_PATH="configurations/service_config.json",
        MONGODB_CLUSTER_URI="localhost:3000",
        LLM_API_KEY="1234567890",
        EMBEDDINGS_API_KEY="1234567890",
    )

    mock_configurations = RagTemplateConfigSchema(
        llm={
            "name": "gpt-3.5-turbo"
        },
        embeddings={
            "name": "embeddings_name"
        },
        vectorStore={
            "dbName": "sample_mflix",
            "collectionName": "movies",
            "indexName": "openai_vector_index",
            "relevanceScoreFn": "euclidean",
            "embeddingKey": "embedding",
            "textKey": "page_content"
        },
        documentation={
            "repository": {
                "baseUrl": "https://api.github.com/repos",
                "owner": "mia-platform",
                "name": "documentation",
                "baseDir": "docs",
                "supportedExtensions": [".md", ".mdx"],
                "requestTimeoutInSeconds": 10
            },
            "website": {
                "baseUrl": "https://docs.mia-platform.eu",
            }
        }
    )

    app_context_params = AppContextParams(
        logger=MagicMock(),
        metrics_manager=MagicMock(),
        env_vars=mock_env_vars,
        configurations=mock_configurations
    )
    return AppContext(params=app_context_params)
