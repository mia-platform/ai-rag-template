from typing import Dict

# Constants related to the vector index
VECTOR_INDEX_TYPE = "vectorSearch"
DEFAULT_NUM_DIMENSIONS_VALUE = 1536

DIMENSIONS_DICT: Dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
