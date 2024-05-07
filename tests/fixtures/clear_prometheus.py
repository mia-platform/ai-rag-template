import pytest
from prometheus_client import REGISTRY


@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    # pylint: disable=W0212
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
