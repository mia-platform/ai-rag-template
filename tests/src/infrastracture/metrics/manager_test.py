from fastapi import Response

from src.infrastracture.metrics.manager import MetricsManager


def test_expose_metrics():
    metrics_manager = MetricsManager()

    response = metrics_manager.expose_metrics()
    body = response.body.decode()

    # Check that the response contains the metrics data
    assert isinstance(response, Response)
    assert "embeddings_tokens_consumed" in body
    assert response.media_type == "text/plain"


def test_embeddings_tokens_consumed_counter():
    metrics_manager = MetricsManager()

    # Increment the counter
    metrics_manager.embeddings_tokens_consumed.inc()

    # Get the metrics data
    response = metrics_manager.expose_metrics()
    metrics_data = response.body.decode()

    # Check that the counter value is correct
    assert "embeddings_tokens_consumed_total 1.0" in metrics_data


def test_embeddings_tokens_consumed_counter_0():
    metrics_manager = MetricsManager()

    # Get the metrics data
    response = metrics_manager.expose_metrics()
    metrics_data = response.body.decode()

    # Check that the counter value is correct
    assert "embeddings_tokens_consumed_total 0.0" in metrics_data
