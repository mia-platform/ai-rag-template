from typing import Any, Dict, Literal
from pydantic import BaseModel


class GenerateEmbeddingsInputSchema(BaseModel):
    url: str
    domain: str | None

class GenerateEmbeddingsOutputSchema(BaseModel):
    state: str
    metadata: Dict[str, Any]

class GenerateStatusOutputSchema(BaseModel):
    status: Literal["running", "idle"]
