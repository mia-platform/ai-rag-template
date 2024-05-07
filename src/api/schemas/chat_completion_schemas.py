# pylint: disable=no-self-argument

from typing import List

from pydantic import BaseModel, validator
from fastapi import HTTPException


class Reference(BaseModel):
    content: str
    url: str


class ChatCompletionInputSchema(BaseModel):
    """
    Represents the input schema for chat completion.

    Attributes:
        chat_query (str): The current query in the chat.
        chat_history (List[str]): The history of the chat messages.
    """
    chat_query: str
    chat_history: List[str]

    @validator('chat_query')
    def validate_chat_query_length(cls, chat_query):
        max_length = 2000
        if len(chat_query) > max_length:
            raise HTTPException(
                status_code=413,
                detail=f'chat_query length exceeds {max_length} characters'
            )
        return chat_query

    @validator('chat_history')
    def validate_chat_history_length(cls, chat_history):
        if len(chat_history) % 2 != 0:
            raise ValueError('chat_history length must be even')
        return chat_history


class ChatCompletionOutputSchema(BaseModel):
    """
    Represents the output schema for chat completion.

    Attributes:
        text (str): The completed message based on the input chat query and history.
        input_documents (List[Document]): List of input documents provided for the completion.
    """
    message: str
    references: List[Reference]
