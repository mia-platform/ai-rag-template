# ai-rag-template

The `ai-rag-template` is a template to build and run your own RAG application to have a Chatbot that is capable to perform a conversation with the user.

<!-- TODO: We use OpenAI, Langchain, MongoDB -->

## Environment Variables

The following environment variables are required for the service to work:

- **PORT**: the port used to expose the API (default: *3000*)
- **LOG_LEVEL**: the level of the logger (default: *INFO*)
- **CONFIGURATION_PATH**: the path that contains the [JSON configuration file](#configuration)
- **MONGODB_CLUSTER_URI**: the MongoDB connectio string
- **LLM_API_KEY**: the API Key of the LLM (*NOTE*: currently, we support only the OpenAI models, thus the API Key is the same as the OpenAI API Key)
- **EMBEDDINGS_API_KEY**: the API Key of the embeddings model (*NOTE*: currently, we support only the OpenAI models, thus the API Key is the same as the OpenAI API Key)

It is suggested to save the environment variables in a `.env` file.

## Configuration

The service requires several configuration parameters for execution. Below is an example configuration:

```json
{
  "llm": {
    "name": "gpt-3.5-turbo"
  },
  "embeddings": {
    "name": "text-embedding-3-small"
  },
  "vectorStore": {
    "dbName": "database-test",
    "collectionName": "assistant-documents",
    "indexName": "vector_index",
    "relevanceScoreFn": "euclidean",
    "embeddingKey": "embedding",
    "textKey": "text",
    "maxDocumentsToRetrieve": 4,
    "minScoreDistance": 0.5
  },
  "chain": {
    "aggregateMaxTokenNumber": 2000,
    "rag": {
      "promptsFilePath": {
        "system": "/path/to/system-prompt.txt",
        "user": "/path/to/user-prompt.txt"
      }
    }
  }
}
```

Description of configuration parameters:

| Name | Key | Description |
|------|-----|-------------|
| LLM Name | `llm.name` | Name of the chat model to use. We currently support only [OpenAI models](https://platform.openai.com/docs/models). |
| Embeddings Name | `embeddings.name` | Name of the encoder to use. We currently support only [OpenAI embeddings models](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings). |
| Vector Store DB Name | `vectorStore.dbName` | Name of the MongoDB database to use as a knowledge base and that contains the collection with the embeddings. |
| Vector Store Collection Name | `vectorStore.collectionName` | Name of the MongoDB collection to use for storing documents and document embeddings. |
| Vector Store Index Name | `vectorStore.indexName` | Name of the vector index to use for retrieving documents related to the user's query. **Note:** [Currently, it's necessary to manually create this index on MongoDB Atlas.](https://www.mongodb.com/docs/atlas/atlas-vector-search/create-index/) |
| Vector Store Relevance Score Function | `vectorStore.relevanceScoreFn` | Name of the similarity function used for extracting similar documents using the created vector index. **Note:** Must be the same used to create the vector index. |
| Vector Store Embeddings Key | `vectorStore.embeddingsKey` | Name of the field used to save the semantic encoding of documents. The question received will be compared to the vector in this field with the Vector Index. |
| Vector Store Text Key | `vectorStore.textKey` | Name of the field used to save the raw document (or chunk of document). The content of this field will be included in the prompt. |
| Vector Store Max. Documents To Retrieve | `vectorStore.maxDocumentsToRetrieve` | Maximum number of documents retrieved from the Vector Store. |
| Vector Store Min. Score Distance | `vectorStore.minScoreDistance` | Minimum score required for the extracted document to be used in the prompt. Any document with a score below this value will be discarded. |
| Chain RAG System Prompts File Path | `vectorStore.textKey` | Path to the file containing system prompts for the RAG model. |
| Chain RAG User Prompts File Path | `vectorStore.textKey` | Path to the file containing user prompts for the RAG model. |

### Create a Vector Index

This template requires a [MongoDB Vector Search Index](https://www.mongodb.com/docs/atlas/atlas-vector-search/tutorials/vector-search-quick-start/) to function correctly, and requires a MongoDB Atlas instance version 6 or above to work.

You can create a new Vector Search Index with the following structure:

```json
{
    "fields": [
        {
            "type": "vector",
            "path": "<<embeddingsKey>>",
            "numDimensions": 768,
            "similarity": "<<relevanceScoreFn>>"
        }
    ]
}
```

You should remember to:

- to have as `path` the same value of the `vectorStore.embeddingsKey` configuration parameter
- to have as `similarity` the same value of the `vectorStore.relevanceScoreFn` configuration parameter
- to have as `numDimensions` to appropriate value based on the [embeddings model used](https://platform.openai.com/docs/guides/embeddings/how-to-get-embeddings)

## API