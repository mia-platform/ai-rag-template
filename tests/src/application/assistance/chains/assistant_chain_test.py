# pylint: disable=too-many-locals
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from src.application.assistance.chains.assistant_chain import AssistantChain
from src.application.assistance.chains.assistant_prompt import AssistantPromptBuilder
from src.application.assistance.chains.combine_docs_chain import AggregateDocsChunksChain
from src.application.assistance.chains.retriever_chain import RetrieverChain, RetrieverChainConfiguration
from tests.src.utils.fake_llm import FakeLLM

# pylint: disable=fixme
# TODO: reduce the duplication in the tests


@patch(
    "src.application.assistance.chains.retriever_chain.RetrieverChain._call",
)
def test_call(mock_retreive_call, app_context, snapshot):
    # Arrange
    # Mocking the dependencies that require connection to external services
    mock_retreive_call.return_value = {"input_documents": [Document(page_content="doc1"), Document(page_content="doc2"), Document(page_content="doc3")]}
    # Atlas and Embeddings
    mock_response = "test response"
    llm = FakeLLM(sequential_responses=True, queries={"1": mock_response})  # LLM service
    # Internal dependencies not mocked
    aggregate_docs_chain = AggregateDocsChunksChain(context=app_context)

    vector_store_configuration = RetrieverChainConfiguration(
        mongodb_cluster_uri="mongodb://localhost:27017",
        db_name="test_db",
        collection_name="test_collection",
        embeddings=OpenAIEmbeddings(openai_api_key="test_api_key", model="test_model"),
        index_name="test_index",
        embedding_key="embedding_key",
        relevance_score_fn="euclidean",
        text_key="page_content",
        max_number_of_results=3,
    )

    retriever_chain = RetrieverChain(context=app_context, configuration=vector_store_configuration)

    assistant_chain = AssistantChain(retriever_chain=retriever_chain, aggregate_docs_chain=aggregate_docs_chain, llm=llm)

    mock_query = "test query"
    mock_chat_history = ["chat message 1", "chat message 2", "chat message 3", "chat message 4"]

    expected_chat_history = "\n".join([("Human: " if i % 2 == 0 else "AI: ") + message for i, message in enumerate(mock_chat_history)])

    expected_chat_history = f"\nReferring to the previous conversation messages:\n\n{expected_chat_history}\n\n---\n"

    inputs = {assistant_chain.query_key: mock_query, assistant_chain.chat_history_key: mock_chat_history}

    expected = {assistant_chain.query_key: mock_query, assistant_chain.chat_history_key: expected_chat_history}

    # Act
    chain_invoked = assistant_chain.invoke(inputs)

    # Assert
    mock_retreive_call.assert_called_once_with(expected)

    assert chain_invoked[assistant_chain.response_key] == mock_response
    assert chain_invoked[assistant_chain.references_key] == mock_retreive_call.return_value["input_documents"]
    assert chain_invoked[assistant_chain.chat_history_key] == expected_chat_history

    # Assert that the last received prompt matches the stored snapshot
    snapshot.assert_match(llm.get_last_received_prompt(), "last_received_prompt")


@patch(
    "src.application.assistance.chains.retriever_chain.RetrieverChain._call",
)
def test_call_without_documents(mock_retreive_call, app_context, snapshot):
    # Arrange
    # Mocking the dependencies that require connection to external services
    mock_retreive_call.return_value = {"input_documents": []}
    # Atlas and Embeddings
    mock_response = "test response"
    llm = FakeLLM(sequential_responses=True, queries={"1": mock_response})  # LLM service
    # Internal dependencies not mocked
    aggregate_docs_chain = AggregateDocsChunksChain(context=app_context)

    vector_store_configuration = RetrieverChainConfiguration(
        mongodb_cluster_uri="mongodb://localhost:27017",
        db_name="test_db",
        collection_name="test_collection",
        embeddings=OpenAIEmbeddings(openai_api_key="test_api_key", model="test_model"),
        index_name="test_index",
        embedding_key="embedding_key",
        relevance_score_fn="euclidean",
        text_key="page_content",
        max_number_of_results=3,
    )

    retriever_chain = RetrieverChain(context=app_context, configuration=vector_store_configuration)

    assistant_chain = AssistantChain(retriever_chain=retriever_chain, aggregate_docs_chain=aggregate_docs_chain, llm=llm)

    mock_query = "test query"
    mock_chat_history = ["chat message 1", "chat message 2", "chat message 3", "chat message 4"]

    expected_chat_history = "\n".join([("Human: " if i % 2 == 0 else "AI: ") + message for i, message in enumerate(mock_chat_history)])

    expected_chat_history = f"\nReferring to the previous conversation messages:\n\n{expected_chat_history}\n\n---\n"

    inputs = {assistant_chain.query_key: mock_query, assistant_chain.chat_history_key: mock_chat_history}

    expected = {assistant_chain.query_key: mock_query, assistant_chain.chat_history_key: expected_chat_history}

    # Act
    chain_invoked = assistant_chain.invoke(inputs)

    # Assert
    mock_retreive_call.assert_called_once_with(expected)

    assert chain_invoked[assistant_chain.response_key] == mock_response
    assert chain_invoked[assistant_chain.references_key] == mock_retreive_call.return_value["input_documents"]
    assert chain_invoked[assistant_chain.chat_history_key] == expected_chat_history

    # Assert that the last received prompt matches the stored snapshot
    snapshot.assert_match(llm.get_last_received_prompt(), "last_received_prompt_without_documents")


@patch(
    "src.application.assistance.chains.retriever_chain.RetrieverChain._call",
)
def test_call_with_custom_prompt(mock_retreive_call, app_context, snapshot):
    # Arrange
    # Mocking the dependencies that require connection to external services
    mock_retreive_call.return_value = {"input_documents": [Document(page_content="doc1"), Document(page_content="doc2"), Document(page_content="doc3")]}
    # Atlas and Embeddings
    mock_response = "test response"
    llm = FakeLLM(sequential_responses=True, queries={"1": mock_response})  # LLM service
    # Internal dependencies not mocked
    aggregate_docs_chain = AggregateDocsChunksChain(context=app_context)

    custom_prompt_builder = AssistantPromptBuilder()
    custom_prompt = (
        custom_prompt_builder.add_variable("a_custom_variable")
        .append_to_system_template("This is a custom prompt with a variable: {a_custom_variable}")
        .build()
    )

    vector_store_configuration = RetrieverChainConfiguration(
        mongodb_cluster_uri="mongodb://localhost:27017",
        db_name="test_db",
        collection_name="test_collection",
        embeddings=OpenAIEmbeddings(openai_api_key="test_api_key", model="test_model"),
        index_name="test_index",
        embedding_key="embedding_key",
        relevance_score_fn="euclidean",
        text_key="page_content",
        max_number_of_results=3,
    )

    retriever_chain = RetrieverChain(context=app_context, configuration=vector_store_configuration)

    assistant_chain = AssistantChain(
        retriever_chain=retriever_chain,
        aggregate_docs_chain=aggregate_docs_chain,
        llm=llm,
        prompt_template=custom_prompt,
    )

    mock_query = "test query"
    mock_chat_history = ["chat message 1", "chat message 2", "chat message 3", "chat message 4"]

    expected_chat_history = "\n".join([("Human: " if i % 2 == 0 else "AI: ") + message for i, message in enumerate(mock_chat_history)])

    expected_chat_history = f"\nReferring to the previous conversation messages:\n\n{expected_chat_history}\n\n---\n"

    inputs = {
        assistant_chain.query_key: mock_query,
        assistant_chain.chat_history_key: mock_chat_history,
        assistant_chain.prompt_custom_variables_key: {"a_custom_variable": "a_custom_value"},
    }

    expected = {
        assistant_chain.query_key: mock_query,
        assistant_chain.chat_history_key: expected_chat_history,
        "a_custom_variable": "a_custom_value",
    }

    # Act
    chain_invoked = assistant_chain.invoke(inputs)

    # Assert
    mock_retreive_call.assert_called_once_with(expected)

    assert chain_invoked[assistant_chain.response_key] == mock_response
    assert chain_invoked[assistant_chain.references_key] == mock_retreive_call.return_value["input_documents"]

    # Assert that the last received prompt matches the stored snapshot
    snapshot.assert_match(llm.get_last_received_prompt(), "last_received_prompt_with_custom_variables")


@patch(
    "src.application.assistance.chains.retriever_chain.RetrieverChain._call",
)
def test_call_without_chat_history(mock_retreive_call, app_context, snapshot):
    # Arrange
    # Mocking the dependencies that require connection to external services
    mock_retreive_call.return_value = {"input_documents": []}
    # Atlas and Embeddings
    mock_response = "test response"
    llm = FakeLLM(sequential_responses=True, queries={"1": mock_response})  # LLM service
    # Internal dependencies not mocked
    aggregate_docs_chain = AggregateDocsChunksChain(context=app_context)

    vector_store_configuration = RetrieverChainConfiguration(
        mongodb_cluster_uri="mongodb://localhost:27017",
        db_name="test_db",
        collection_name="test_collection",
        embeddings=OpenAIEmbeddings(openai_api_key="test_api_key", model="test_model"),
        index_name="test_index",
        embedding_key="embedding_key",
        relevance_score_fn="euclidean",
        text_key="page_content",
        max_number_of_results=3,
    )

    retriever_chain = RetrieverChain(context=app_context, configuration=vector_store_configuration)

    assistant_chain = AssistantChain(retriever_chain=retriever_chain, aggregate_docs_chain=aggregate_docs_chain, llm=llm)

    mock_query = "test query"
    mock_chat_history = []

    expected_chat_history = ""

    inputs = {assistant_chain.query_key: mock_query, assistant_chain.chat_history_key: mock_chat_history}

    expected = {assistant_chain.query_key: mock_query, assistant_chain.chat_history_key: expected_chat_history}

    # Act
    chain_invoked = assistant_chain.invoke(inputs)

    # Assert
    mock_retreive_call.assert_called_once_with(expected)

    assert chain_invoked[assistant_chain.response_key] == mock_response
    assert chain_invoked[assistant_chain.references_key] == mock_retreive_call.return_value["input_documents"]
    assert chain_invoked[assistant_chain.chat_history_key] == expected_chat_history

    # Assert that the last received prompt matches the stored snapshot
    snapshot.assert_match(llm.get_last_received_prompt(), "last_received_prompt_without_chat_history")
