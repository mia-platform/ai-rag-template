import json
from unittest.mock import patch
from pathlib import Path
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from httpx import Response

from src.application.assistance.chains.retriever_chain import RetrieverChain, RetrieverChainConfiguration


def load_json_response(file_name):
    current_dir = Path(__file__).parent.parent
    file_path = current_dir / "assets" / file_name

    with open(file_path, "r", encoding="utf-8") as opened_file:
        return json.loads(opened_file.read())

def setup_test(
    app_context,
    mock_server,
    max_score_distance=None,
    min_score_distance=None
):
    mock_similar_documents = [
        (Document(page_content="doc1"), 0.5),
        (Document(page_content="doc2"), 0.5),
        (Document(page_content="doc3"), 0.5)
    ]

    mock_query = "test query"

    embedding_reply_mock = load_json_response("openai_embedding.json")

    mock_server\
        .respx_mock\
        .post("https://api.openai.com/v1/embeddings")\
        .mock(return_value=Response(
            200,
            json=embedding_reply_mock))

    vector_store_configuration = RetrieverChainConfiguration(
        mongodb_cluster_uri="mongodb://localhost:27017",
        db_name="test_db",
        collection_name="test_collection",
        embeddings=OpenAIEmbeddings(
            openai_api_key="test_api_key",
            model="test_model"
        ),
        index_name="test_index",
        embedding_key="embedding_key",
        relevance_score_fn="euclidean",
        text_key="page_content",
        max_number_of_results=3,
        max_score_distance=max_score_distance,
        min_score_distance=min_score_distance
    )

    chain = RetrieverChain(
        context=app_context,
        configuration=vector_store_configuration
    )

    inputs = {
        chain.query_key: mock_query,
    }


    return mock_similar_documents, inputs, chain

@patch(
    'langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch._similarity_search_with_score',
)
def test_call(
    similarity_search_with_score,
    app_context,
    mock_server,
):
    # Arrange
    mock_similar_documents, inputs, chain = setup_test(app_context, mock_server)
    similarity_search_with_score.return_value = mock_similar_documents

    # Act
    result = chain.invoke(inputs)

    # Assert
    assert result[chain.output_key] == [
        doc for doc, _ in mock_similar_documents]
    for doc, _ in mock_similar_documents:
        # pylint: disable=E1136
        assert doc.metadata['score'] == 0.5
        
@patch(
    'langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch._similarity_search_with_score',
)
def test_call_with_max_distance(
    similarity_search_with_score,
    app_context,
    mock_server,
):
    # Arrange
    mock_similar_documents, inputs, chain = setup_test(app_context, mock_server, max_score_distance=0.5)
    similarity_search_with_score.return_value = mock_similar_documents

    # Act
    chain.invoke(inputs)

    # Assert that the similarity_search_with_score method was called with the expected parameters
    post_filter_call_arg = similarity_search_with_score.call_args[1]["post_filter_pipeline"]
    assert post_filter_call_arg[0]["$match"]["score"]["$lte"] == 0.5

@patch(
    'langchain_community.vectorstores.mongodb_atlas.MongoDBAtlasVectorSearch._similarity_search_with_score',
)
def test_call_with_min_distance(
    similarity_search_with_score,
    app_context,
    mock_server,
):
    # Arrange
    mock_similar_documents, inputs, chain = setup_test(app_context, mock_server, min_score_distance=0.5)
    similarity_search_with_score.return_value = mock_similar_documents

    # Act
    chain.invoke(inputs)

    # Assert that the similarity_search_with_score method was called with the expected parameters
    post_filter_call_arg = similarity_search_with_score.call_args[1]["post_filter_pipeline"]
    assert post_filter_call_arg[0]["$match"]["score"]["$gte"] == 0.5
