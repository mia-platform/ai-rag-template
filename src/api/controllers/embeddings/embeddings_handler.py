import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from src.api.schemas.status_ok_schema import StatusOkResponseSchema
from src.application.embeddings.embedding_generator import EmbeddingGenerator
from src.api.schemas.embeddings_schemas import GenerateEmbeddingsInputSchema
from src.context import AppContext

router = APIRouter()

lock = asyncio.Lock()

async def generate_embeddings_from_url(url: str, app_context: AppContext):
    """
    Generate embeddings for a given URL.
    """
    embedding_generator = EmbeddingGenerator(app_context=app_context)
    await embedding_generator.crawl(url)

@router.post(
    "/embeddings/generate",
    response_model=StatusOkResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Embeddings"]
)
async def generate_embeddings(request: Request, data: GenerateEmbeddingsInputSchema, background_tasks: BackgroundTasks):
    """
    Generate embeddings for a given URL.
    """

    request_context: AppContext = request.state.app_context
    url = data.url
    request_context.logger.info(f"Generate embeddings request received for url: {url}")

    if lock.locked():
        request_context.logger.info("Generation embeddings process already in progress.")

        raise HTTPException(status_code=409, detail="A process to generate embeddings is already in progress.")

    async with lock:
        background_tasks.add_task(generate_embeddings_from_url, url, request_context)

    request_context.logger.info("Generation embeddings process started.")
    return {"statusOk": True}

@router.get(
    "/embeddings/status",
    response_model=StatusOkResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Embeddings"]
)
async def embeddings_status():
    """
    Get the status of the embeddings generation process.
    """
    if lock.locked():
        raise HTTPException(status_code=409, detail="A process to generate embeddings is already in progress.")

    return {"statusOk": True}
