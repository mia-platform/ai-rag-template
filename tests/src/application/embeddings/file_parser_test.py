import io
from pathlib import Path
from zipfile import BadZipFile

from fastapi import UploadFile
import pytest

from src.constants import (
    GZIP_CONTENT_TYPE,
    MD_CONTENT_TYPE,
    PDF_CONTENT_TYPE,
    TAR_CONTENT_TYPE,
    TEXT_CONTENT_TYPE,
    ZIP_CONTENT_TYPE
)
from src.application.embeddings.errors import InvalidFileExtensionError
from src.application.embeddings.file_parser import FileParser

ASSETS_FOLDER = "assets"

TXT_FILE_NAME = "text_file.txt"
MARKDOWN_FILE_NAME = "markdown_file.md"
PDF_FILE_NAME = "pdf_file.pdf"
ZIP_FILE_NAME = "zip_file.zip"
TAR_FILE_NAME = "tar_file.tar"
GZIP_FILE_NAME = "tar_gz_file.tar.gz"

TXT_FILE_CONTENT = 'this is a text file\n'
MARKDOWN_FILE_CONTENT = '# Markdown File\n\nThis is a Markdown file\n'
PDF_FILE_CONTENT = "this is a PDF (portable document format) file\n"

def test_extract_document_from_text_file(logger):
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / TXT_FILE_NAME, 'rb') as txt_file:
        upload_file = UploadFile(
            filename=TXT_FILE_NAME,
            headers={"content-type": TEXT_CONTENT_TYPE},
            file=txt_file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes only one document, the txt document
        assert len(result) == 1
        assert result[0] == TXT_FILE_CONTENT


def test_extract_document_from_markdown_file(logger):
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / MARKDOWN_FILE_NAME, 'rb') as markdown_file:
        upload_file = UploadFile(
            filename=MARKDOWN_FILE_NAME,
            headers={"content-type": MD_CONTENT_TYPE},
            file=markdown_file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes only one document, the md document
        assert len(result) == 1
        assert result[0] == MARKDOWN_FILE_CONTENT


def test_extract_document_from_pdf_file(logger):
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / PDF_FILE_NAME, 'rb') as pdf_file_binary:
        upload_file = UploadFile(
            filename=PDF_FILE_NAME,
            headers={"content-type": PDF_CONTENT_TYPE},
            file=pdf_file_binary,
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes only one document, the txt document
        assert len(result) == 1
        assert result[0] == PDF_FILE_CONTENT


def test_extract_documents_from_zip_file_test(logger):
        # We are passing a zip file that contains, in this order:
        # - a markdown file
        # - a text file
        # - a pdf file
        # We check that the split_text and the add_documents is called 3 times with the correct text passed as argument
    
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / ZIP_FILE_NAME, 'rb') as zip_file:
        upload_file = UploadFile(
            filename=ZIP_FILE_NAME,
            headers={"content-type": ZIP_CONTENT_TYPE},
            file=zip_file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes the text_content, the markdown_content and pdf_content
        assert len(result) == 3
        assert result[0] == MARKDOWN_FILE_CONTENT
        assert result[1] == PDF_FILE_CONTENT
        assert result[2] == TXT_FILE_CONTENT


def test_extract_documents_from_tar_file_test(logger):
        # We are passing a tar file that contains, in this order:
        # - a markdown file
        # - a text file
        # - a pdf file
        # We check that the split_text and the add_documents is called 3 times with the correct text passed as argument
    
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / TAR_FILE_NAME, 'rb') as tar_file:
        upload_file = UploadFile(
            filename=TAR_FILE_NAME,
            headers={"content-type": TAR_CONTENT_TYPE},
            file=tar_file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes the text_content, the markdown_content and pdf_content
        assert len(result) == 3
        assert result[0] == MARKDOWN_FILE_CONTENT
        assert result[1] == PDF_FILE_CONTENT
        assert result[2] == TXT_FILE_CONTENT


def test_extract_documents_from_tar_gz_file_test(logger):
        # We are passing a gz file that contains, in this order:
        # - a markdown file
        # - a text file
        # - a pdf file
        # We check that the split_text and the add_documents is called 3 times with the correct text passed as argument
    
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / GZIP_FILE_NAME, 'rb') as tar_gz_file:
        upload_file = UploadFile(
            filename=GZIP_FILE_NAME,
            headers={"content-type": GZIP_CONTENT_TYPE},
            file=tar_gz_file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes the text_content, the markdown_content and pdf_content
        assert len(result) == 3
        assert result[0] == MARKDOWN_FILE_CONTENT
        assert result[1] == PDF_FILE_CONTENT
        assert result[2] == TXT_FILE_CONTENT


def test_fail_open_file_with_wrong_extension(logger):
    upload_file = UploadFile(
        filename="image_png.png",
        headers={"content-type": "image/png"},
        file=io.BytesIO(b"this is an image")
    )

    file_parser = FileParser(logger)

    with pytest.raises(InvalidFileExtensionError):
        document_generator = file_parser.extract_documents_from_file(upload_file)
        for _ in document_generator:
            # We are not supposed to get here
            pass
            

def test_fail_if_non_valid_zip_file(logger):
    upload_file = UploadFile(
        filename="not_a_zip_file.zip",
        headers={"content-type": "application/zip"},
        file=io.BytesIO(b"this is a text file")
    )

    file_parser = FileParser(logger)

    with pytest.raises(BadZipFile):
        document_generator = file_parser.extract_documents_from_file(upload_file)
        for _ in document_generator:
            # We are not supposed to get here
            pass
