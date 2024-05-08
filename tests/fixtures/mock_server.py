import pytest
import httpretty


class MockServer():
    """
    A simple mock server for testing purposes.
    """

    def __init__(self, respx_mock) -> None:
        self._respx_mock = respx_mock

    def enable(self):
        self._respx_mock.start()
        httpretty.enable(verbose=False, allow_net_connect=False)

    def disable(self):
        self._respx_mock.clear()
        self._respx_mock.reset()
        self._respx_mock.stop()
        httpretty.reset()
        httpretty.disable()

    # pylint: disable=R0913
    def register_uri(
        self,
        method,
        uri,
        body='{"message": "HTTPretty :)"}',
        adding_headers=None,
        forcing_headers=None,
        status=200,
        responses=None,
        match_querystring=False,
        priority=0,
        **headers
    ):
        httpretty.register_uri(
            method,
            uri,
            body,
            adding_headers,
            forcing_headers,
            status,
            responses,
            match_querystring,
            priority,
            **headers
        )

    @property
    def respx_mock(self):
        return self._respx_mock


@pytest.fixture
def mock_server(respx_mock):
    """
    This server is a utility that can be used to run a simple mock of an external service
    """
    server = MockServer(respx_mock=respx_mock)
    server.enable()

    yield server

    server.disable()
