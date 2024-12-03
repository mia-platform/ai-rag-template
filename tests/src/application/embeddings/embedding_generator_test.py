from pathlib import Path
from unittest.mock import patch
from fastapi import UploadFile
import requests_mock

from src.application.embeddings.embedding_generator import EmbeddingGenerator


TEXT_HTML_HEADERS = {'Content-type': 'text/html'}
IMAGE_PNG_HEADERS = {'Content-type': 'image/png'}


def test_generate_from_url_without_domain(app_context):
    current_dir = Path(__file__).parent
    file_path = current_dir / "assets" / "html_page_without_links.html"
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://example.com', headers=TEXT_HTML_HEADERS, text=html_content)

        with patch("langchain_experimental.text_splitter.SemanticChunker.split_text") as mock_split_text, \
            patch('langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch.add_documents') as mock_add_documents:

            mock_split_text.return_value = ["chunk1", "chunk2"]

            embedding_generator = EmbeddingGenerator(app_context)
            embedding_generator.generate_from_url("http://example.com")

            mock_split_text.assert_called_once()
            mock_add_documents.assert_called_once()
            embedding_generator.logger.debug.assert_called()


def test_generate_from_url_with_domain(app_context):
    current_dir = Path(__file__).parent
    with open(current_dir / "assets" / "html_page_without_links.html", 'r', encoding='utf-8') as f:
        html_page_without_links_content = f.read()
    with open(current_dir / "assets" / "html_page_with_links.html", 'r', encoding='utf-8') as f:
        html_page_with_links_content = f.read()

    with requests_mock.Mocker() as mocker:
        mocker.get('http://example.com', headers=TEXT_HTML_HEADERS, text=html_page_with_links_content)
        mocker.get('http://example.com/domain/page', headers=TEXT_HTML_HEADERS, text=html_page_without_links_content)
        mocker.get('http://example.com/domain/img.png', headers=IMAGE_PNG_HEADERS, text='I shouldn\'t be here')

        with patch("langchain_experimental.text_splitter.SemanticChunker.split_text") as mock_split_text, \
            patch('langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch.add_documents') as mock_add_documents:

            mock_split_text.return_value = ["chunk1", "chunk2"]

            embedding_generator = EmbeddingGenerator(app_context)
            embedding_generator.generate_from_url("http://example.com", filter_path="http://example.com/domain")

            assert mock_split_text.call_count == 2
            assert mock_add_documents.call_count == 2
            embedding_generator.logger.debug.assert_called()


def test_generate_from_zip_file(app_context):
        # We are passing a zip file that contains:
        # - a text file
        # - a markdown file
        # - a pdf file
        # We check that the split_text and the add_documents is called 3 times with the correct text passed as argument
    
    current_dir = Path(__file__).parent

    with patch("langchain_experimental.text_splitter.SemanticChunker.split_text") as mock_split_text, \
        patch('langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch.add_documents') as mock_add_documents, \
        open(current_dir / "assets" / "zip_file.zip", 'rb') as zip_file:
        
        upload_file = UploadFile(
            filename="zip_file.zip",
            headers={'Content-Type': 'application/zip'},
            file=zip_file,
        )

        embedding_generator = EmbeddingGenerator(app_context)
        embedding_generator.generate_from_file(upload_file)

        assert mock_split_text.call_count == 3
        assert mock_add_documents.call_count == 3
        embedding_generator.logger.debug.assert_called()

        mock_split_text.assert_any_call('this is a text file\n')
        mock_split_text.assert_any_call('# Markdown File\nThis is a Markdown file\n')
        mock_split_text.assert_any_call('this is a PDF (portable document format) file\n')
