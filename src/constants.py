from typing import Dict

# Constants related to the vector index
VECTOR_INDEX_TYPE = "vectorSearch"
DEFAULT_NUM_DIMENSIONS_VALUE = 1536

DIMENSIONS_DICT: Dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}

# Constants related to the embeddings generation via uploaded file

ZIP_EXTENSION = '.zip'
PDF_EXTENSION = '.pdf'
TEXT_EXTENSION = '.txt'
MD_EXTENSION = '.md'

SUPPORTED_FILES_TUPLE = (ZIP_EXTENSION, PDF_EXTENSION, TEXT_EXTENSION, MD_EXTENSION)
SUPPORTED_FILES_IN_ZIP_TUPLE = (PDF_EXTENSION, TEXT_EXTENSION, MD_EXTENSION)
