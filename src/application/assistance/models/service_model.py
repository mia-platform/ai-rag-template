from langchain_core.documents import Document
from pydantic.v1 import BaseModel


class ChatCompletionModel(BaseModel):
    response: str
    references: list[Document]
