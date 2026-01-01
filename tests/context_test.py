from logging import Logger

from starlette.requests import Request

HEADER_TO_PROXY = [
    "miauserid",
    "miausergroups",
    "miaclienttype",
    "isbackoffice",
    "x-forwarded-for",
    "x-forwarded-host",
    "request-id",
    "x-request-id",
]

HEADER_NOT_TO_PROXY = "not_to_proxy"


def test_create_request_context(app_context):
    app_context.env_vars.HEADERS_TO_PROXY = ",".join(HEADER_TO_PROXY)

    mock_headers = {
        "miauserid": "123",
        "miausergroups": "admin",
        "miaclienttype": "web",
        "isbackoffice": "true",
        "not_to_proxy": HEADER_NOT_TO_PROXY,
    }

    mock_request = Request(
        scope={"type": "http", "headers": [(k.encode(), v.encode()) for k, v in mock_headers.items()]},
        receive=None,
        send=None,
    )

    mock_request_logger = Logger("request_logger")

    # Act
    decorated_app_context = app_context.create_request_context(request_logger=mock_request_logger, request=mock_request)

    # Assert
    assert decorated_app_context.logger == mock_request_logger
    assert decorated_app_context.request_context.headers_to_proxy == {
        "miauserid": "123",
        "miausergroups": "admin",
        "miaclienttype": "web",
        "isbackoffice": "true",
    }
    assert decorated_app_context.configurations == app_context.configurations
    assert decorated_app_context.env_vars == app_context.env_vars
