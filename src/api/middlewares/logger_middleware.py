import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_ID_HEADER = "x-request-id"

class ReqIdLoggerAdapter(logging.LoggerAdapter):
    """
    Logger Adapter to add reqid to the log records.
    """

    def process(self, msg, kwargs):
        if "extra" in kwargs:
            kwargs["extra"]["reqId"] = self.extra["reqId"]
        return msg, kwargs

class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add the logger to the request and logs request info
    """

    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request, call_next):
        excluded_paths = [
            '/-/ready',
            '/-/healthz',
            '/-/check-up',
            '/-/metrics',
        ]
        
        request_id = request.headers.get(REQUEST_ID_HEADER, '')
        request_logger = ReqIdLoggerAdapter(self.logger, {'reqId': request_id})

        if request.url.path not in excluded_paths:
            request_logger.info(
                f"{request.method} {request.url.path}",
                extra={
                    "http": {
                        "method": request.method,
                        "path": request.url.path,
                    }
                }
            )
            start_time = time.time()

        request.state.logger = request_logger
        response = await call_next(request)

        if request.url.path not in excluded_paths:
            duration = time.time() - start_time
            request_logger.info(
                f"{request.method} {request.url.path}",
                extra={
                    "http": {
                        "method": request.method,
                        "path": request.url.path,
                        "status": response.status_code,
                        "duration": duration,   
                    }
                }
            )

        return response
