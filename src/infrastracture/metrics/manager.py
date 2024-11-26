# pylint: disable=W0511
from prometheus_client import Counter, generate_latest
from fastapi import Response

class MetricsManager:
    def __init__(self): # TODO: add namespace
        self._embeddings_tokens_consumed = Counter(
            'embeddings_tokens_consumed',
            'Number of embeddings tokens consumed',
            namespace='console' # TODO: add to configurations
        )
        self._requests_tokens_consumed = Counter(
            'requests_tokens_consumed',
            'Number of requests tokens consumed',
            namespace='console' # TODO: add to configurations
        )
        self._reply_tokens_consumed = Counter(
            'reply_tokens_consumed',
            'Number of reply tokens consumed',
            namespace='console' # TODO: add to configurations
        )
        self._ingestion_tokens_consumed = Counter(
            'ingestion_tokens_consumed',
            'Number of ingestion tokens consumed',
            namespace='console' # TODO: add to configurations
        )

    @property
    def embeddings_tokens_consumed(self) -> Counter:
        """Counter representing the total number of tokens consumed by the embeddings model."""
        return self._embeddings_tokens_consumed

    @property
    def reply_tokens_consumed(self) -> Counter:
        """Counter representing the total number of tokens consumed when generating replies."""
        return self._reply_tokens_consumed
    
    @property
    def requests_tokens_consumed(self) -> Counter:
        """Counter representing the total number of tokens consumed when making requests."""
        return self._requests_tokens_consumed

    @property
    def ingestion_tokens_consumed(self) -> Counter:
        """Counter representing the total number of tokens consumed during the data ingestion process."""
        return self._ingestion_tokens_consumed

    def expose_metrics(self) -> Response:
        """Generate and return the metrics for Prometheus scraping."""
        metrics_data = generate_latest()

        return Response(content=metrics_data, media_type="text/plain")
