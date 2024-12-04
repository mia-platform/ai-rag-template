
from src.constants import SUPPORTED_EXT_TUPLE


class InvalidFileExtensionError(Exception):
    """
        Exception raised when a file does not have the expected extension.

        Consider that only the following extensions are supported:
        - text files (.txt files)
        - markdown files(.md files)
        - PDF files (.pdf files)
        - archive files (.zip files, *.tar files or *.gz files) that includes only the above extensions.
    """
    def __init__(self, filename):
        self.message = f"The file {filename} cannot be processed. Supported extensions are: {", ".join(SUPPORTED_EXT_TUPLE)}."
        super().__init__(self.message)
