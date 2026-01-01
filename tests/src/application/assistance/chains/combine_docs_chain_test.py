import pytest
from langchain_core.documents import Document

from src.application.assistance.chains.combine_docs_chain import AggregateDocsChunksChain


def test_instance_creation(app_context):
    try:
        instance = AggregateDocsChunksChain(context=app_context)
        assert isinstance(instance, AggregateDocsChunksChain)
    # pylint: disable=W0703
    except Exception:
        pytest.fail("Creating instance of AggregateDocsChunksChain failed")


def test_combine_docs_run_chain(app_context, snapshot):
    docs = [Document(page_content="doc1"), Document(page_content="doc2"), Document(page_content="doc3")]

    chain = AggregateDocsChunksChain(
        context=app_context,
    )

    result = chain.invoke({chain.input_key: docs})

    snapshot.assert_match(result[chain.output_key], "combine_docs_chain_result")


def test_combine_docs_exceeds_max_tokens(app_context):
    # Create a list of mock Document objects with long page_content
    docs = [Document(page_content="doc1" * 1000), Document(page_content="doc2" * 1000)]

    # Create an instance of AggregateDocsChunksChain
    chain = AggregateDocsChunksChain(context=app_context)

    chain.invoke({chain.input_key: docs})

    # Check that a warning was logged
    app_context.logger.warning.assert_called_with(f"Combined text length exceeded {chain.aggregate_max_token_number} tokens")
