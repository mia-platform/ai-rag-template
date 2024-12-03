import base64
import io
from logging import Logger
from tempfile import TemporaryDirectory

from typing import Generator
from zipfile import BadZipFile, ZipFile
import fitz
from fastapi import File, UploadFile

from src.constants import MD_EXTENSION, PDF_EXTENSION, SUPPORTED_FILES_IN_ZIP_TUPLE, SUPPORTED_FILES_TUPLE, TEXT_EXTENSION, ZIP_EXTENSION
from src.application.embeddings.errors import InvalidFileExtensionError


class FileParser:
    # TODO: Add documentation
    # TODO: Add logs
    
    def __init__(self, logger: Logger):
        self.logger = logger

    def _convert_bytes_to_str(self, content: bytes) -> str:
        return content.decode("utf-8")

    def _convert_text_to_str(self, file: UploadFile = File(...)) -> str:
        try:
            content = file.file.read()
            return self._convert_bytes_to_str(content)
        except UnicodeDecodeError:
            content = base64.b64encode(file.file.read())
            return self._convert_bytes_to_str(content)
        
    def _convert_from_doc_to_str(self, doc: open) -> Generator[str, None, None]:
        # TODO: Test this with more complicated PDFs, because to_markdown seems not working
        # We could've used:
        # return pymupdf4llm.to_markdown(doc)
        # return pymupdf.get_text(doc)

        for page in doc:
            yield page.get_text()

    def _convert_pdf_to_str(self, file: UploadFile) -> Generator[str, None, None]:
        doc = fitz.open(file.file)
        yield from self._convert_from_doc_to_str(doc)
    
    def extract_documents_from_zip_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        try:
            content = file.file.read()
            with (
                TemporaryDirectory() as temp_dir,
                ZipFile(io.BytesIO(content)) as zipf
            ):
                zipf.extractall(temp_dir)

                # Check for the list of file: we extract the files then we check if the extension match the available ones (supported: pdf, txt, md)
                for file_name in zipf.namelist():
                    # NOTE: For now we do not support folders inside zip files. Should we?
                    if file_name.endswith(SUPPORTED_FILES_IN_ZIP_TUPLE):
                        with zipf.open(file_name) as f:
                            file_content = f.read()

                            if file_name.endswith(PDF_EXTENSION):
                                doc = fitz.open(stream=file_content)
                                yield from self._convert_from_doc_to_str(doc)
                            if file_name.endswith(TEXT_EXTENSION):
                                yield self._convert_bytes_to_str(file_content)
                            if file_name.endswith(MD_EXTENSION):
                                yield self._convert_bytes_to_str(file_content)
        except BadZipFile as bad_zip_file_ex:
            self.logger.error(bad_zip_file_ex)
            raise BadZipFile(bad_zip_file_ex)
        except Exception as ex:
            self.logger.error(ex)
            raise Exception(f"An error occurred while extracting the file {file.filename}")

        
    
    def extract_documents_from_file(self, file: UploadFile = File(...)) -> Generator[str, None, None]:
        if not file.filename.endswith(SUPPORTED_FILES_TUPLE):
            raise InvalidFileExtensionError(filename=file.filename)
        
        result: list[str] = []
        if file.filename.endswith(PDF_EXTENSION):
            result = list(self._convert_pdf_to_str(file))
        if file.filename.endswith(TEXT_EXTENSION):
            result = [self._convert_text_to_str(file)]
        if file.filename.endswith(MD_EXTENSION):
            result = [self._convert_text_to_str(file)]
        if file.filename.endswith(ZIP_EXTENSION):
            result = list(self.extract_documents_from_zip_file(file))
    
        yield from result
        
    
