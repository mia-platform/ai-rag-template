from typing import Any, Literal

from pydantic import BaseModel


class GenerateEmbeddingsInputSchema(BaseModel):
    url: str
    filterPath: str | None = None


class GenerateEmbeddingsOutputSchema(BaseModel):
    state: str
    metadata: dict[str, Any]


class GenerateStatusOutputSchema(BaseModel):
    status: Literal["running", "idle"]
