from fastapi import APIRouter, Request, status

from src.api.schemas.chat_completion_schemas import (
    ChatCompletionInputSchema, ChatCompletionOutputSchema)
from src.application.assistance.service import AssistantService, AssistantServiceChatCompletionResponse
from src.context import AppContext

router = APIRouter()


@router.post(
    "/chat/completions",
    response_model=ChatCompletionOutputSchema,
    status_code=status.HTTP_200_OK,
    tags=["RAG-template"]
)
async def chat_completions(request: Request, chat: ChatCompletionInputSchema):
    """
    Handles chat completions by generating responses to user queries, taking into account the context provided in the chat history. Retrieves relevant information from the configured vector store to formulate responses.
    """

    request_context: AppContext = request.state.app_context

    request_context.logger.info("Chat completions request received")

    assistant_service = AssistantService(
        app_context=request_context
    )

    completion_response = assistant_service.chat_completion(
        query=chat.chat_query,
        chat_history=chat.chat_history
    )
    
    request_context.logger.info("Chat completions request completed")


    return response_mapper(completion_response)


def response_mapper(completion_response: AssistantServiceChatCompletionResponse):
    message = completion_response.response
    references = [
        {
            "content": doc.page_content,
            "url": doc.metadata["url"]
        }
        for doc in completion_response.references
    ]

    return {
        "message": message,
        "references": references
    }
