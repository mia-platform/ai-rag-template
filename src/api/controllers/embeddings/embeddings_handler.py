from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from src.api.schemas.status_ok_schema import StatusOkResponseSchema
from src.application.embeddings.embedding_generator import EmbeddingGenerator
from src.api.schemas.embeddings_schemas import GenerateEmbeddingsInputSchema, GenerateStatusOutputSchema
from src.context import AppContext

router = APIRouter()

# This is a simplified mechanism to prevent multiple requests from generating embeddings at the same time.
# For this specific router, we designed it to only allow one request to generate embeddings at a time, therefore
# we use a lock to prevent multiple requests from starting the process at the same time.
#
# In case of need of multiple methods that requires locking or very long tasks,
# you might want to use a more sophisticated mechanism to handle this.
router.lock = False

def generate_embeddings_from_url_background_task(app_context: AppContext, url: str, filter_path: str | None):
    """
    Generate embeddings for a given URL. 
    
    This method is intended to be called as a background task. Includes managmement of the lock mechanism
    of this router, which is locked when the embedding generation process is running, and unlocked when it finishes.

    Args:
        app_context (AppContext): The application context.
        url (str): The URL to generate embeddings from.
        filter_path (str | None): The full domain to compare the hyperlinks against.
    """
    logger = app_context.logger

    try:
        router.lock = True
        embedding_generator = EmbeddingGenerator(app_context=app_context)
        embedding_generator.generate_from_url(url, filter_path)
    # pylint: disable=W0718
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
def generate_embeddings_from_url(request: Request, data: GenerateEmbeddingsInputSchema, background_tasks: BackgroundTasks):
    """
    Generate embeddings for a given URL. It starts from a single web page and generates embeddings for the text data of that page and
    for every page connected via hyperlinks (anchor tags).

    This method can be run only one at a time, as it uses a lock to prevent multiple requests from starting the process at the same time.
    If a process is already in progress, it will return a 409 status code (Conflict).

    The embeddings are generated only from the text of each web page: images, rss and any other webpage with a ContextType different from text/html
    are not included.

    The POST requests require a body that includes:

    - url: The URL to generate embeddings from.
    - filterPath: The full domain to compare the hyperlinks against.

    Args:
        request (Request): The request object.
        data (GenerateEmbeddingsInputSchema): The input schema.
        background_tasks (BackgroundTasks): The background tasks object.
    """

    request_context: AppContext = request.state.app_context
    url = data.url
    filter_path = data.filterPath
    request_context.logger.info(f"Generate embeddings request received for url: {url}")

    if not router.lock:
        background_tasks.add_task(generate_embeddings_from_url_background_task, request_context, url, filter_path)
        request_context.logger.info("Generation embeddings process started.")
        return {"statusOk": True}
    
    raise HTTPException(status_code=409, detail="A process to generate embeddings is already in progress.")

@router.get(
    "/embeddings/status",
    response_model=GenerateStatusOutputSchema,
    status_code=status.HTTP_200_OK,
    tags=["Embeddings"]
)
def embeddings_status():
    """
    Get the status of the embeddings generation process.

    Returns:
        dict: A `status` object that can be either "running" (if a process is ongoing) or "idle" (if the service is ready).
    """
    return {"status": "running" if router.lock else "idle"}
