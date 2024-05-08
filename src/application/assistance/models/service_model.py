from pydantic.v1 import BaseModel
from langchain_core.documents import Document


class ChatCompletionModel(BaseModel):
    response: str
    references: list[Document]
