from unittest.mock import patch

from langchain_openai import OpenAIEmbeddings

from src.application.embeddings.document_chunker import DocumentChunker


def test_split_text_into_chunks():
    with patch("langchain_experimental.text_splitter.SemanticChunker.split_text") as mock_split_text:
        mock_split_text.return_value = ["This is a test.", "this is another test."]
        embedding = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key="embeddings_api_key")
        document_chunker = DocumentChunker(embedding)
        text = "This is a test. This is another test."
        url = "http://example.com"
        chunks = document_chunker.split_text_into_chunks(text, url)

        assert mock_split_text.call_count == 1
        assert len(chunks) == 2
