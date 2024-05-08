from fastapi import APIRouter, Request, status
from fastapi.responses import PlainTextResponse

from src.context import AppContext


router = APIRouter()


@router.get(
    "/-/metrics",
    response_class=PlainTextResponse,
    status_code=status.HTTP_200_OK,
    tags=["RAG-template"]
)
async def metrics(request: Request):
    """
    Handles metrics requests by logging the request body and returning a 200 OK response.
    """

    app_context: AppContext = request.state.app_context
    metrics_manager = app_context.metrics_manager
    
    return metrics_manager.expose_metrics()
