from typing import Generator
from zipfile import BadZipFile
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile, status

from src.constants import MD_CONTENT_TYPE, PDF_CONTENT_TYPE, ZIP_CONTENT_TYPE, TEXT_CONTENT_TYPE
from src.api.schemas.status_ok_schema import StatusOkResponseSchema
from src.application.embeddings.embedding_generator import EmbeddingGenerator
from src.application.embeddings.file_parser import FileParser
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
        logger.debug("Locking router for embedding generation.")
        router.lock = True
        embedding_generator = EmbeddingGenerator(app_context=app_context)
        logger.info("Starting embedding generation process.")
        embedding_generator.generate_from_url(url, filter_path)
        logger.info("Embedding generation process finished.")
    # pylint: disable=W0718
    except Exception as e:
        logger.error(f"Error in background task: {str(e)}")
    finally:
        router.lock = False
        logger.debug("Router unlocked after embedding generation.")

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

def generate_embeddings_from_file_background_task(app_context: AppContext, document_generator: Generator[str, None, None]):
    """
    Generate embeddings for an uploaded file. 
    
    This method is intended to be called as a background task. Includes managmement of the lock mechanism
    of this router, which is locked when the embedding generation process is running, and unlocked when it finishes.

    Args:
        app_context (AppContext): The application context.
        file (UploadFile): The file to extract the embeddings from.
    """
    logger = app_context.logger

    try:
        logger.debug("Locking router for embedding generation.")
        router.lock = True
        embedding_generator = EmbeddingGenerator(app_context=app_context)
        logger.info("Starting embedding generation process.")
        for doc in document_generator:
            embedding_generator.generate_from_text(doc)
        logger.info("Embedding generation process finished.")
    # pylint: disable=W0718
    except Exception as ex:
        logger.error(ex)
        logger.error(f"Error in background task: {str(ex)}")
    finally:
        router.lock = False
        logger.debug("Router unlocked after embedding generation.")

@router.post(
    "/embeddings/generateFromFile",
    response_model=StatusOkResponseSchema,
    status_code=status.HTTP_200_OK,
    tags=["Embeddings"]
)
def generate_embeddings_from_file(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Generate embeddings for a given file. 
    
    The file must be uploaded with content type "multipart/form-data" request and must have one of the following content type:
        - text/plain (such as .txt files)
        - text/markdown (such as .md files)
        - application/pdf
        - application/zip (which must contain only file of the previous types)

    Args:
        request (Request): The request object.
        file (UploadFile): The file received.
        background_tasks (BackgroundTasks): The background tasks object.
    """

    if file.content_type not in [MD_CONTENT_TYPE, TEXT_CONTENT_TYPE, PDF_CONTENT_TYPE, ZIP_CONTENT_TYPE]:
        raise HTTPException(status_code=400, detail=f"Application does not support this file type (content type: {file.content_type}).")
    
    request_context: AppContext = request.state.app_context
    request_context.logger.info(f"Generate embeddings request received for file {file.filename} (content type: {file.content_type})")
    
    try:
        file_parser = FileParser(request_context.logger)
        docs = list(file_parser.extract_documents_from_file(file))
    except BadZipFile as ex:
        raise HTTPException(status_code=400, detail="File uploaded is not a valid application/zip file.") from ex
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(ex)}") from ex

    if not router.lock:
        background_tasks.add_task(generate_embeddings_from_file_background_task, request_context, docs)
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
