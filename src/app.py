import uvicorn
from fastapi import FastAPI

from src.api.controllers.chat_completions import chat_completions_handler
from src.api.controllers.core.checkup import checkup_handler
from src.api.controllers.core.liveness import liveness_handler
from src.api.controllers.core.metrics import metrics_handler
from src.api.controllers.core.readiness import readiness_handler
from src.api.controllers.embeddings import embeddings_handler
from src.api.middlewares.app_context_middleware import AppContextMiddleware
from src.api.middlewares.logger_middleware import LoggerMiddleware
from src.configurations.configuration import get_configuration
from src.configurations.variables import get_variables
from src.context import AppContext, AppContextParams
from src.infrastracture.logger import get_logger
from src.infrastracture.metrics.manager import MetricsManager
from src.lib.vector_search_index_updater import VectorSearchIndexUpdater


def create_app(context: AppContext) -> FastAPI:
    app = FastAPI(openapi_url="/documentation/json", redoc_url=None, title="ai-rag-template", version="0.5.3")

    app.add_middleware(AppContextMiddleware, app_context=context)
    app.add_middleware(LoggerMiddleware, logger=context.logger)

    app.include_router(liveness_handler.router)
    app.include_router(readiness_handler.router)
    app.include_router(checkup_handler.router)
    app.include_router(metrics_handler.router)

    app.include_router(chat_completions_handler.router)
    app.include_router(embeddings_handler.router)

    return app


if __name__ == "__main__":
    logger = get_logger()
    metrics_manager = MetricsManager()
    env_vars = get_variables(logger)
    configurations = get_configuration(env_vars.CONFIGURATION_PATH, logger)

    app_context = AppContext(params=AppContextParams(logger=logger, metrics_manager=metrics_manager, env_vars=env_vars, configurations=configurations))

    application = create_app(app_context)

    vector_search_index_updater = VectorSearchIndexUpdater(app_context)
    vector_search_index_updater.update_vector_search_index()

    uvicorn.run(
        application,
        host="0.0.0.0",  # nosec B104 # binding to all interfaces is required to expose the service in containers
        port=int(app_context.env_vars.PORT),
        log_level="error",
    )
