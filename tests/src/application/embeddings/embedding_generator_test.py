from pathlib import Path
from unittest.mock import patch

from src.application.embeddings.embedding_generator import EmbeddingGenerator


def test_generate(app_context):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / "example.html"
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    with patch('requests.api.get') as mock_requests_get, \
        patch("langchain_experimental.text_splitter.SemanticChunker.split_text") as mock_split_text, \
        patch('langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch.add_documents') as mock_add_documents:

        embedding_generator = EmbeddingGenerator(app_context)

        mock_requests_get.return_value.text = html_content
        mock_split_text.return_value = ["chunk1", "chunk2"]

        embedding_generator.generate("http://example.com")

        mock_split_text.assert_called_once()
        mock_add_documents.assert_called_once()
        embedding_generator.logger.debug.assert_called()
