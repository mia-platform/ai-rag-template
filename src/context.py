from logging import Logger

from attr import dataclass
from starlette.requests import Request

from src.configurations.service_model import RagTemplateConfigSchema
from src.configurations.variables_model import Variables
from src.infrastracture.metrics.manager import MetricsManager


class RequestContext:
    def __init__(self, logger: Logger, env_vars: Variables, request: Request):
        self._logger = logger
        if request:
            self._headers_to_proxy = self._build_proxy_headers(env_vars, request)

    def _build_proxy_headers(self, env_vars: Variables, request: Request):
        # Extract headers from the request where the header name is in the HEADERS_TO_PROXY list in the environment variables
        if not env_vars.HEADERS_TO_PROXY:
            return {}
        headers_to_proxy = env_vars.HEADERS_TO_PROXY.split(",")
        headers = {}
        for header in headers_to_proxy:
            if header in request.headers:
                headers[header] = request.headers[header]

        return headers

    @property
    def logger(self):
        return self._logger

    @property
    def headers_to_proxy(self):
        return self._headers_to_proxy


@dataclass
class AppContextParams:
    logger: Logger
    metrics_manager: MetricsManager
    env_vars: Variables
    configurations: RagTemplateConfigSchema
    request_context: RequestContext | None = None


class AppContext:
    """
    The AppContext class serves as a container for key components used across the application.

    It holds instances of the logger, metrics manager, environment variables, and configurations,  allowing these
    instances to be shared and easily accessed throughout the application.
    """

    def __init__(self, params: AppContextParams):
        self._logger = params.logger
        self._metrics_manager = params.metrics_manager
        self._env_vars = params.env_vars
        self._configurations = params.configurations
        self._request_context = params.request_context if params.request_context else None

    @property
    def logger(self):
        return self._logger

    @property
    def metrics_manager(self):
        return self._metrics_manager

    @property
    def env_vars(self):
        return self._env_vars

    @property
    def configurations(self):
        return self._configurations

    @property
    def request_context(self):
        return self._request_context

    def create_request_context(self, request_logger, request: Request = None):
        """
        Creates a new AppContext with a different logger instance, while keeping references to the original context creating a new request context.
        """
        params = AppContextParams(
            logger=request_logger,
            metrics_manager=self._metrics_manager,
            env_vars=self._env_vars,
            configurations=self._configurations,
            request_context=RequestContext(logger=request_logger, env_vars=self._env_vars, request=request if request else None),
        )
        return AppContext(params)
