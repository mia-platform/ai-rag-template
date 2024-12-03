
from src.constants import SUPPORTED_FILES_TUPLE


class InvalidFileExtensionError(Exception):
    """
        Exception raised when a file does not have the expected extension.

        Consider that only the following extensions are supported:
        - archive files (.zip files)
        - text files (.txt files)
        - markdown files(.md files)
        - PDF files (.pdf files)
    """
    def __init__(self, filename):
        self.message = f"The file {filename} cannot be processed. Supported extensions are: {", ".join(SUPPORTED_FILES_TUPLE)}."
        super().__init__(self.message)
