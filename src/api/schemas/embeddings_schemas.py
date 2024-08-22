from typing import Any, Dict
from pydantic import BaseModel


class GenerateEmbeddingsInputSchema(BaseModel):
    url: str

class GenerateEmbeddingsOutputSchema(BaseModel):
    state: str
    metadata: Dict[str, Any]
