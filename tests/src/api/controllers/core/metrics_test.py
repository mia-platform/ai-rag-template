
from fastapi.testclient import TestClient
from src.app import create_app
from src.context import AppContext, AppContextParams
from src.infrastracture.metrics.manager import MetricsManager


def test_metrics_handler(app_context):
    
    app_context_params = AppContextParams(
        logger=app_context.logger,
        metrics_manager=MetricsManager(),
        env_vars=app_context.env_vars,
        configurations=app_context.configurations
    )
    
    mock_app_context = AppContext(params=app_context_params)
    
    test_app = create_app(mock_app_context)
    
    with TestClient(test_app) as client:
        response = client.get(
            "/-/metrics",
        )
        
        # retrieve the metrics data from the response body
        metrics_data = response.text
        
        assert response.status_code == 200
        assert 'embeddings_tokens_consumed_total 0.0' in metrics_data
