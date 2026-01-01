import gzip
import io
import tarfile
from collections.abc import Generator
from logging import Logger
from tempfile import TemporaryDirectory
from typing import IO
from zipfile import BadZipFile, ZipFile

from fastapi import File, UploadFile
from pymupdf import Document

from src.application.embeddings.file_parser.errors import InvalidFileError
from src.application.embeddings.file_parser.get_file_type import FileType, get_file_type
from src.constants import (
    MD_EXTENSION,
    MDX_EXTENSION,
    PDF_EXTENSION,
    SUPPORTED_EXT_IN_COMPRESSED_FILE_TUPLE,
    TEXT_EXTENSION,
)


class FileParser:
    """
    A utility class for parsing and converting different types of files to string format.

        This class provides methods to handle various file types including:
        - Text files (.txt)
        - Markdown files (.md)
        - PDF files (.pdf)
        - ZIP archives containing supported file types

        The parser can:
        - Convert text and markdown files to strings
        - Extract text content from PDF files
        - Process ZIP files and extract supported file types within them
        - Handle file content encoding and conversion

        Args:
            logger (Logger): A logger instance for tracking operations and debugging
    """

    def __init__(self, logger: Logger):
        self.logger = logger

    def _convert_bytes_to_str(self, content: bytes) -> str:
        return content.decode("utf-8")

    def _convert_text_to_str(self, file: UploadFile = File(...)) -> str:
        self.logger.debug(f"Converting text file {file.filename} to string...")
        content = file.file.read()
        return self._convert_bytes_to_str(content)

    def _convert_from_doc_to_str(self, doc: Document) -> Generator[str, None, None]:
        for page in doc:
            yield page.get_text()

    def _convert_pdf_to_str(self, file: UploadFile) -> Generator[str, None, None]:
        self.logger.debug(f"Extracting text from PDF file {file.filename}")
        file_content = file.file.read()
        doc = Document(stream=file_content)
        yield from self._convert_from_doc_to_str(doc)

    def _convert_file_to_str(self, file: IO[bytes], file_name: str) -> Generator[str, None, None]:
        file_content = file.read()
        file_extension = file_name.split(".")[-1]

        if file_extension == PDF_EXTENSION:
            doc = Document(stream=file_content)
            yield from self._convert_from_doc_to_str(doc)
        elif file_extension == TEXT_EXTENSION:
            yield self._convert_bytes_to_str(file_content)
        elif file_extension in (MD_EXTENSION, MDX_EXTENSION):
            yield self._convert_bytes_to_str(file_content)

    def _extract_documents_from_zip_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        self.logger.debug(f"Extracting files from zip file {file.filename}")
        try:
            content = file.file.read()
            with TemporaryDirectory() as temp_dir, ZipFile(io.BytesIO(content)) as zipf:
                zipf.extractall(path=temp_dir, members=zipf.namelist())

                self.logger.info(f"Extracted {len(zipf.namelist())} files. Processing them...")

                # Check for the list of file: we extract the files then we check if the extension match the available ones (supported: pdf, txt, md)
                for file_name in zipf.namelist():
                    # For now we do not support folders inside zip files.
                    if file_name.endswith(SUPPORTED_EXT_IN_COMPRESSED_FILE_TUPLE):
                        with zipf.open(file_name) as f:
                            self.logger.info(f"Reading file {file_name}")
                            yield from self._convert_file_to_str(f, file_name)
        except BadZipFile as bad_zip_file_ex:
            self.logger.error(bad_zip_file_ex)
            raise BadZipFile(bad_zip_file_ex)
        except Exception as ex:
            # pylint: disable=W0719
            raise Exception(f"An error occurred while extracting the file {file.filename}") from ex

    def _extract_documents_from_tar_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        self.logger.debug(f"Extracting files from tar file {file.filename}")
        try:
            content = file.file.read()
            with TemporaryDirectory() as temp_dir, tarfile.open(fileobj=io.BytesIO(content)) as tarf:
                tarf.extractall(path=temp_dir, filter="data")
                self.logger.info(f"Extracted {len(tarf.getmembers())} files. Processing them...")

                # Process each file in the tar archive
                for member in tarf.getmembers():
                    # Skip if it's a directory
                    if member.isfile() and member.name.endswith(SUPPORTED_EXT_IN_COMPRESSED_FILE_TUPLE):
                        with tarf.extractfile(member) as f:
                            self.logger.info(f"Reading file {member.name}")
                            yield from self._convert_file_to_str(f, member.name)
        except tarfile.TarError as tar_error:
            self.logger.error(tar_error)
            raise tarfile.TarError(f"Invalid tar file: {tar_error}")
        except Exception as ex:
            # pylint: disable=W0719
            raise Exception(f"An error occurred while extracting the file {file.filename}") from ex

    def _extract_documents_from_gzip_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        self.logger.debug(f"Extracting files from gzip file {file.filename}")
        try:
            content = file.file.read()
            with TemporaryDirectory() as temp_dir, gzip.open(io.BytesIO(content)) as gzf:
                # For .tar.gz files
                if file.filename.endswith(".tar.gz"):
                    with tarfile.open(fileobj=gzf) as tarf:
                        tarf.extractall(path=temp_dir, filter="data")
                        self.logger.info(f"Extracted {len(tarf.getmembers())} files. Processing them...")

                        for member in tarf.getmembers():
                            if member.isfile() and member.name.endswith(SUPPORTED_EXT_IN_COMPRESSED_FILE_TUPLE):
                                with tarf.extractfile(member) as f:
                                    self.logger.info(f"Reading file {member.name}")
                                    yield from self._convert_file_to_str(f, member.name)
                # For single .gz files
                else:
                    decompressed_content = gzf.read()
                    if file.filename.endswith(".pdf.gz"):
                        doc = Document(stream=decompressed_content)
                        yield from self._convert_from_doc_to_str(doc)
                    elif file.filename.endswith((".txt.gz", ".md.gz")):
                        yield self._convert_bytes_to_str(decompressed_content)

        except gzip.BadGzipFile as gzip_error:
            self.logger.error(gzip_error)
            raise gzip.BadGzipFile(f"Invalid gzip file: {gzip_error}")
        except Exception as ex:
            # pylint: disable=W0719
            raise Exception(f"An error occurred while extracting the file {file.filename}") from ex

    def extract_documents_from_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        """
        Extract text content from various file types and return it as a Generator.

        This method supports extracting text from `pdf`s, `txt`s, `md`s, and archive files (`zip`, `tar` and `gz` supported).
        For archives, it will process all supported file types contained within.
        This is performed with a check on the file content-type

        The use of a Generator allows for memory-efficient processing of large files by yielding content
        incrementally rather than loading everything into memory at once. It can be transformed into a list
        using the `list()` function or simply iterated over.

        Args:
            file (UploadFile): The file to process, supported formats are PDF, TXT, MD, and ZIP

        Returns:
            Generator[str, None, None]: A generator that yields strings of text content

        Raises:
            InvalidFileError: If the file extension is not supported
            BadZipFile: If the zip file is corrupted or invalid
            TarError: If the tar file is corrupted or invalid
            BadGzipFile: If the gzip file is corrupted or invalid
            Exception: For general processing errors

        """
        self.logger.info(f"Extracting documents from file {file.filename}")

        file_type = get_file_type(file)

        if file_type is None:
            raise InvalidFileError(filename=file.filename)

        result: list[str] | Generator[str, None, None] = []

        match file_type:
            case FileType.TEXT:
                result = [self._convert_text_to_str(file)]
            case FileType.PDF:
                result = self._convert_pdf_to_str(file)
            case FileType.ZIP:
                result = self._extract_documents_from_zip_file(file)
            case FileType.TAR:
                result = self._extract_documents_from_tar_file(file)
            case FileType.GZIP:
                result = self._extract_documents_from_gzip_file(file)
            case _:
                raise InvalidFileError(filename=file.filename)

        self.logger.info(f"Completed documents extraction from file {file.filename}")
        yield from result
