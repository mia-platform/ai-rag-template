from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from src.api.schemas.status_ok_schema import StatusOkResponseSchema
from src.application.embeddings.embedding_generator import EmbeddingGenerator
from src.api.schemas.embeddings_schemas import GenerateEmbeddingsInputSchema
from src.context import AppContext

router = APIRouter()

# This is a simplified mechanism to prevent multiple requests from generating embeddings at the same time.
# For this specific router, we designed it to only allow one request to generate embeddings at a time, therefore
# we use a lock to prevent multiple requests from starting the process at the same time.
#
# In case of need of multiple methods that requires locking or very long tasks,
# you might want to use a more sophisticated mechanism to handle this.
router.lock = False

def generate_embeddings_from_url(url: str, app_context: AppContext):
    """
    Generate embeddings for a given URL.
    """
    logger = app_context.logger

    try:
        router.lock = True
        embedding_generator = EmbeddingGenerator(app_context=app_context)
        embedding_generator.generate(url)
    except Exception as e:
        logger.error(f"Error in background task: {str(e)}")
    finally:
        router.lock = False

@router.post(
    "/embeddings/generate",
    response_model=StatusOkResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Embeddings"]
)
def generate_embeddings(request: Request, data: GenerateEmbeddingsInputSchema, background_tasks: BackgroundTasks):
    """
    Generate embeddings for a given URL.

    This method can be run only one at a time, as it uses a lock to prevent multiple requests from starting the process at the same time.
    If a process is already in progress, it will return a 409 status code (Conflict).

    Args:
        request (Request): The request object.
        data (GenerateEmbeddingsInputSchema): The input schema.
        background_tasks (BackgroundTasks): The background tasks object.
    """

    request_context: AppContext = request.state.app_context
    url = data.url
    request_context.logger.info(f"Generate embeddings request received for url: {url}")

    if not router.lock:
        background_tasks.add_task(generate_embeddings_from_url, url, request_context)
        request_context.logger.info("Generation embeddings process started.")
        return {"statusOk": True}
    
    raise HTTPException(status_code=409, detail="A process to generate embeddings is already in progress.")

@router.get(
    "/embeddings/status",
    response_model=StatusOkResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Embeddings"]
)
def embeddings_status():
    """
    Get the status of the embeddings generation process.

    Returns:
        dict: A StatusOkResponseSchema responding _True_.
        
    Raises:
        HTTPException: If a process to generate embeddings is already in progress (thus: the lock is on _True_).
    """
    if router.lock:
        raise HTTPException(status_code=409, detail="A process to generate embeddings is already in progress.")

    return {"statusOk": True}
