from unittest.mock import MagicMock, call, patch

from src.lib.vector_search_index_updater import VectorSearchIndexUpdater


def test_update_vector_index_requires_no_changes(app_context):
    '''
    app_context (from `/tests/fixtures/app_context.py`) includes:
    - vectorStore.indexName = "openai_vector_index"
    - vectorStore.relevanceScoreFn = "euclidean" (which means that the index must have "similarity" equal to "euclidean")
    - embeddings.name = "text-emebedding-3-small" (which means that the index must have "numDimensions" equal to 1536)

    The mock should not receive instruction to update the index "openai_vector_index" since there won't be any changes on its definition.
    '''
    with (
        patch("pymongo.collection.Collection") as mock_collection,
        patch("pymongo.MongoClient.__new__") as mock_client,
    ):
        mock_client.return_value = {"sample_mflix": {"movies": mock_collection}}

        mock_collection.list_search_indexes.return_value = [
            {"name": "another_vector_index", "latestDefinition": {"fields": []}},
            {
                "name": "openai_vector_index",
                "latestDefinition": {
                    "fields": [
                        {"numDimensions": 1536, "path": "embedding", "similarity": "euclidean", "type": "vector"}
                    ]
                },
            },
        ]

        vector_search_index_updater = VectorSearchIndexUpdater(app_context)
        vector_search_index_updater.update_vector_search_index()

        mock_collection.list_search_indexes.assert_called_once()
        mock_collection.create_search_index.assert_not_called()
        mock_collection.update_search_index.assert_not_called()

        info_log_calls = [
            call('Check of MongoDB Vector Search index "openai_vector_index"'),
            call("Vector Search index is up-to-date, no further action required"),
        ]
        app_context.logger.info.assert_has_calls(info_log_calls, any_order=True)
        app_context.logger.warn.assert_not_called()


def test_update_vector_index_requires_create(app_context):
    """
    Since there's no vector index in the collection named "openai_vector_index", the mock should receive instruction to create the index.
    """
    with patch("pymongo.collection.Collection") as mock_collection, patch("pymongo.MongoClient.__new__") as mock_client:
        mock_client.return_value = {"sample_mflix": {"movies": mock_collection}}
        mock_collection.list_search_indexes.return_value = []
        mock_collection.create_search_index = MagicMock()

        vector_search_index_updater = VectorSearchIndexUpdater(app_context)
        vector_search_index_updater.update_vector_search_index()

        mock_collection.list_search_indexes.assert_called_once()
        mock_collection.create_search_index.assert_called_once()
        mock_collection.update_search_index.assert_not_called()

        info_log_calls = [
            call('Vector Search index "openai_vector_index" missing, it will be created now'),
            call('Created Vector Search index "openai_vector_index"'),
        ]
        app_context.logger.info.assert_has_calls(info_log_calls, any_order=True)


def test_update_vector_index_requires_update(app_context):
    '''
    app_context (from `/tests/fixtures/app_context.py`) includes:
    - vectorStore.indexName = "openai_vector_index"
    - vectorStore.relevanceScoreFn = "euclidean" (which means that the index must have "similarity" equal to "euclidean")
    - embeddings.name = "text-emebedding-3-small" (which means that the index must have "numDimensions" equal to 1536)

    The mock should receive instruction to update the index named "openai_vector_index" since both "similarity" and "numDimensions" must be updated.
    '''
    with patch("pymongo.collection.Collection") as mock_collection, patch("pymongo.MongoClient.__new__") as mock_client:
        mock_client.return_value = {"sample_mflix": {"movies": mock_collection}}

        mock_collection.list_search_indexes.return_value = [
            {
                "name": "openai_vector_index",
                "latestDefinition": {
                    "fields": [{"numDimensions": 3072, "path": "embedding", "similarity": "cosine", "type": "vector"}, {"path": "__STATE__", "type": "filter"}]
                },
            }
        ]

        vector_search_index_updater = VectorSearchIndexUpdater(app_context)
        vector_search_index_updater.update_vector_search_index()

        mock_collection.list_search_indexes.assert_called_once()
        mock_collection.create_search_index.assert_not_called()
        mock_collection.update_search_index.assert_called_once()

        info_log_calls = [
            call('Check of MongoDB Vector Search index "openai_vector_index"'),
            call('Updated Vector Search index "openai_vector_index"'),
        ]
        app_context.logger.info.assert_has_calls(info_log_calls, any_order=True)
