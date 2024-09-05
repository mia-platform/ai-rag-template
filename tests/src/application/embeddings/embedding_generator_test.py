from pathlib import Path
from unittest.mock import patch

import requests
import requests_mock

from src.application.embeddings.embedding_generator import EmbeddingGenerator


def test_generate(app_context):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / "example.html"
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Initializing mock
    session = requests.Session()
    adapter = requests_mock.Adapter()

    session.mount('http://', adapter)
    adapter.register_uri('GET', 'http://example.com', text=html_content)

    with patch("langchain_experimental.text_splitter.SemanticChunker.split_text") as mock_split_text, \
        patch('langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch.add_documents') as mock_add_documents:
        mock_split_text.return_value = ["chunk1", "chunk2"]

        embedding_generator = EmbeddingGenerator(app_context)
        embedding_generator.generate("http://example.com")

        mock_split_text.assert_called_once()
        mock_add_documents.assert_called_once()
        embedding_generator.logger.debug.assert_called()
