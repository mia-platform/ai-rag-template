from starlette.middleware.base import BaseHTTPMiddleware

from src.context import AppContext


class AppContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject a custom application context into the Starlette app state
    """

    def __init__(self, app, app_context: AppContext):
        super().__init__(app)
        self.app_context = app_context

    async def dispatch(self, request, call_next):
        excluded_paths = [
            '/-/ready',
            '/-/healthz',
            '/-/check-up'
        ]

        if request.url.path not in excluded_paths:
            request.state.app_context = self.app_context.create_request_context(
                request.state.logger,
                request=request
            )

        response = await call_next(request)

        return response
