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
from src.application.embeddings.errors import InvalidFileError
from src.application.embeddings.file_parser.file_parser import FileParser

ASSETS_FOLDER = "assets"

TXT_FILE_NAME = "text_file.txt"
MD_FILE_NAME = "markdown_file.md"
MDX_FILE_NAME = "markdown_file.mdx"
PDF_FILE_NAME = "pdf_file.pdf"
ZIP_FILE_NAME = "zip_file.zip"
TAR_FILE_NAME = "tar_file.tar"
GZIP_FILE_NAME = "tar_gz_file.tar.gz"

TXT_FILE_CONTENT = 'this is a text file\n'
MD_FILE_CONTENT = '# Markdown File\n\nThis is a Markdown file\n'
MDX_FILE_CONTENT = '# Markdown File\n\nThis is a Markdown file\n\n## Code example\n\n```javascript\nconst message = "Hello, world!";\nconsole.log(message);\n```\n'
PDF_FILE_CONTENT = "this is a PDF (portable document format) file\n"

@pytest.mark.parametrize(
        "file_name, file_content_type, file_content",
        [
            (TXT_FILE_NAME, TEXT_CONTENT_TYPE, TXT_FILE_CONTENT),
            (MD_FILE_NAME, MD_CONTENT_TYPE, MD_FILE_CONTENT),
            (MD_FILE_NAME, None, MD_FILE_CONTENT),
            (MDX_FILE_NAME, "application/javascript", MDX_FILE_CONTENT),
            (PDF_FILE_NAME, PDF_CONTENT_TYPE, PDF_FILE_CONTENT),
        ]
)
def test_extract_document_from_non_compressed_file(logger, file_name, file_content_type, file_content):
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / file_name, 'rb') as file:
        upload_file = UploadFile(
            filename=file_name,
            headers={"content-type": file_content_type},
            file=file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes only one document, the txt document
        assert len(result) == 1
        assert result[0] == file_content


def test_fail_open_file_with_wrong_extension(logger):
    upload_file = UploadFile(
        filename="image_png.png",
        headers={"content-type": "image/png"},
        file=io.BytesIO(b"this is an image")
    )

    file_parser = FileParser(logger)

    with pytest.raises(InvalidFileError):
        document_generator = file_parser.extract_documents_from_file(upload_file)
        for _ in document_generator:
            # We are not supposed to get here
            pass


@pytest.mark.parametrize(
        "file_name, file_content_type",
        [
            (ZIP_FILE_NAME, ZIP_CONTENT_TYPE),
            (TAR_FILE_NAME, TAR_CONTENT_TYPE),
            (GZIP_FILE_NAME, GZIP_CONTENT_TYPE),
        ]
)
def test_extract_documents_from_compressed_file_test(logger, file_name, file_content_type):
        # We are passing a compressed file that contains, in this order:
        # - a markdown file
        # - a text file
        # - a pdf file
        # We check that the split_text and the add_documents is called 3 times with the correct text passed as argument
    
    current_dir = Path(__file__).parent

    with open(current_dir / ASSETS_FOLDER / file_name, 'rb') as file:
        upload_file = UploadFile(
            filename=file_name,
            headers={"content-type": file_content_type},
            file=file
        )

        file_parser = FileParser(logger)
        result = list(file_parser.extract_documents_from_file(upload_file))

        # check that the result list includes the text_content, the markdown_content and pdf_content
        assert len(result) == 3
        assert result[0] == MD_FILE_CONTENT
        assert result[1] == PDF_FILE_CONTENT
        assert result[2] == TXT_FILE_CONTENT
            

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
