import io
from logging import Logger
from tempfile import TemporaryDirectory

from typing import Generator
from zipfile import BadZipFile, ZipFile
from pymupdf import Document
from fastapi import File, UploadFile

from src.constants import MD_EXTENSION, PDF_EXTENSION, SUPPORTED_FILES_IN_ZIP_TUPLE, SUPPORTED_FILES_TUPLE, TEXT_EXTENSION, ZIP_EXTENSION
from src.application.embeddings.errors import InvalidFileExtensionError


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
        self.logger.debug(f'Extracting text from PDF file {file.filename}')
        file_content = file.file.read()
        doc = Document(stream=file_content)
        yield from self._convert_from_doc_to_str(doc)
    
    def _extract_documents_from_zip_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        self.logger.debug(f'Extracting files from zip file {file.filename}')
        try:
            content = file.file.read()
            with (
                TemporaryDirectory() as temp_dir,
                ZipFile(io.BytesIO(content)) as zipf
            ):
                zipf.extractall(temp_dir)

                self.logger.info(f'Extracted {len(zipf.namelist())} files. Processing them...')

                # Check for the list of file: we extract the files then we check if the extension match the available ones (supported: pdf, txt, md)
                for file_name in zipf.namelist():
                    # For now we do not support folders inside zip files.
                    if file_name.endswith(SUPPORTED_FILES_IN_ZIP_TUPLE):
                        with zipf.open(file_name) as f:
                            self.logger.info(f'Reading file {file_name}')
                            file_content = f.read()

                            if file_name.endswith(PDF_EXTENSION):
                                doc = Document(stream=file_content)
                                yield from self._convert_from_doc_to_str(doc)
                            if file_name.endswith(TEXT_EXTENSION):
                                yield self._convert_bytes_to_str(file_content)
                            if file_name.endswith(MD_EXTENSION):
                                yield self._convert_bytes_to_str(file_content)
        except BadZipFile as bad_zip_file_ex:
            self.logger.error(bad_zip_file_ex)
            raise BadZipFile(bad_zip_file_ex)
        except Exception as ex:
            #pylint: disable=W0719
            raise Exception(f"An error occurred while extracting the file {file.filename}") from ex

        
    
    def extract_documents_from_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        """
        Extract text content from various file types and return it as a Generator.
                
        This method supports extracting text from PDF, TXT, MD, and ZIP files. For ZIP files,
        it will process all supported file types contained within. 
        
        The use of a Generator allows for memory-efficient processing of large files by yielding content
        incrementally rather than loading everything into memory at once. It can be transformed into a list
        using the `list()` function or simply iterated over.
        
        Args:
            file (UploadFile): The file to process, supported formats are PDF, TXT, MD, and ZIP
            
        Returns:
            Generator[str, None, None]: A generator that yields strings of text content
            
        Raises:
            InvalidFileExtensionError: If the file extension is not supported
            BadZipFile: If the ZIP file is corrupted or invalid
            Exception: For general processing errors
        
        """
        self.logger.info(f"Extracting documents from file {file.filename}")
        if not file.filename.endswith(SUPPORTED_FILES_TUPLE):
            raise InvalidFileExtensionError(filename=file.filename)
        
        result: list[str] | Generator[str, None, None] = []
        if file.filename.endswith(PDF_EXTENSION):
            result = self._convert_pdf_to_str(file)
        if file.filename.endswith((TEXT_EXTENSION, MD_EXTENSION)):
            # Since we are returning a Generator (an iterable), we need to convert it to a list
            result = [self._convert_text_to_str(file)]
        if file.filename.endswith(ZIP_EXTENSION):
            result = self._extract_documents_from_zip_file(file)
    
        self.logger.info(f"Completed documents extraction from file {file.filename}")
        yield from result
