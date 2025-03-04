# ai-rag-template

[![Python
version](https://img.shields.io/badge/python-v3.12.3-blue)](.coverage/html/index.html)
[![FastAPI
version](https://img.shields.io/badge/fastapi-v0.115.6-blue)](.coverage/html/index.html)

---

`ai-rag-template` is a template meant to be a based for the implementation of a RAG (retrieval augmented generation) system.  
This repository contains the backend code, which consists of a web server that provides REST APIs to primarily support one type of operation:

- **Chat**: Provides a conversation feature, allowing users to ask questions and get responses from the chatbot.

The backend was developed using the [LangChain](https://python.langchain.com/docs/get_started/introduction/) framework, which enables creating sequences of complex interactions using Large Language Models. The web server was implemented using the [FastAPI](https://fastapi.tiangolo.com/) framework.

More information on how the service works can be found in the [Overview and Usage](./docs/10_Overview_And_Usage.md) page.

## Main Features

When running the service, the application exposes a Swagger UI at the `/docs` endpoint.

### Chat Endpoint (`/chat/completions`)

The `/chat/completions` endpoint generates responses to user queries based on provided context and chat history. It leverages information from the configured Vector Store to formulate relevant responses, enhancing the conversational experience.

***Example***:

<details>
<summary>Request</summary>

```curl
curl 'http://localhost:3000/chat/completions' \
  -H 'content-type: application/json' \
  --data-raw '{"chat_query":"Design a CRUD schema for an online store selling merchandise items","chat_history":[]}'
```

</details>

<details>
<summary>Response</summary>

```json
{
    "message": "For an online store selling merchandise items, we can design a CRUD schema for a `Product` entity with the following properties: ...",
    "references": [
        {
            "content": "### Create CRUD to Read and Write Table Data  \n...",
            "url": "https://docs.mia-platform.eu/docs/microfrontend-composer/tutorials/basics"
        },
        {
            "content": "### Create CRUD to Read and Write Table Data  \n...",
            "url": "https://docs.mia-platform.eu/docs/microfrontend-composer/tutorials/basics"
        },
        {
            "content": "### Create a CRUD for persistency  \n...",
            "url": "https://docs.mia-platform.eu/docs/console/tutorials/configure-marketplace-components/flow-manager"
        },
        {
            "content": "### Create a CRUD for persistency  \n...",
            "url": "https://docs.mia-platform.eu/docs/console/tutorials/configure-marketplace-components/flow-manager"
        }
    ]
}
```

</details>

### Embedding Endpoints

#### Generate from website (`/embeddings/generate`)

The `/embeddings/generate` endpoint is a HTTP POST method that takes as input:

- `url` (string, *required*), a web URL used as a starting point
- `filterPath` (string, not required), a more specific web URL that the one specified above

- crawl the webpage
- check for links on the same domain (and, if included, that begins with the `filterPath`) of the webpage and store them in a list
- scrape the page for text
- generate the embeddings using the [configured embedding model](#configuration)
- start again from every link still in the list

> **NOTE**:
> This method can be run only one at a time, as it uses a lock to prevent multiple requests from starting the process at the same time.
>
> No information are returned when the process ends, either as completed or stopped because of an error.

***Eg***:

<details>
<summary>Request</summary>

```curl
curl 'http://localhost:3000/embedding/generate' \
  -H 'content-type: application/json' \
  --data-raw '{"url":"https://docs.mia-platform.eu/", "domain": "https://docs.mia-platform.eu/docs/runtime_suite_templates" }'
```

</details>

<details>
<summary>Response in case the runner is idle</summary>

```json
200 OK
{
    "statusOk": "true"
}
```
</details>

<details>
<summary>Response in case the runner is running</summary>

```json
409 Conflict
{
    "detail": "A process to generate embeddings is already in progress." 
}
```
</details>

#### Generate from file (`/embeddings/generateFromFile`)

The `/embeddings/generateFromFile` endpoint is a HTTP POST method that takes as input:

- `file` (binary, *required*), a file to be uploaded containing the text that will be transformed into embeddings.

The file must be of format:

- a text file (`.txt`)
- a markdown file (`.md` or `.mdx`)
- a PDF file (`.pdf`)
- a zip file (formats available: `.zip`, `.tar`, `.gz`) containing files of the same formats as above (folders and other files will be skipped).

For this file, of each file inside the archive, the text will be retrieved, chunked and the embeddings generated.

> **NOTE**:
> This method can be run only one at a time, as it uses a lock to prevent multiple requests from starting the process at the same time.
>
> No information are returned when the process ends, either as completed or stopped because of an error.

***Eg***:

<details>
<summary>Request</summary>

```curl
curl -X 'POST' \
  'https://rag-app-test.console.gcp.mia-platform.eu/api/embeddings/generateFromFile' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@my-archive.zip;type=application/zip'
```

</details>

<details>
<summary>Response in case the runner is idle</summary>

```json
200 OK
{
    "statusOk": "true"
}
```
</details>

<details>
<summary>Response in case the runner is running</summary>

```json
409 Conflict
{
    "detail": "A process to generate embeddings is already in progress." 
}
```
</details>

#### Generation status (`/embeddings/status`)

This request returns to the user information regarding the [embeddings generation runner](#generate-embedding-endpoint-embeddingsgenerate). Could be either `idle` (no process currently running) or `running` (a process of generating embeddings is actually happenning).

***Eg***:

<details>
<summary>Request</summary>

```curl
curl 'http://localhost:3000/embedding/status' \
  -H 'content-type: application/json' \
```

</details>

<details>
<summary>Response</summary>

```json
200 OK
{
    "status": "idle"
}
```
</details>

### Metrics Endpoint (`/-/metrics`)

The `/-/metrics` endpoint exposes the metrics collected by Prometheus.

## High Level Architecture

The following is the high-level architecture of ai-rag-template.

```mermaid
flowchart LR
  fe[Frontend]
  be[Backend]
  vs[(Vector Store)]
  llm[LLM API]
  eg[Embeddings Generator API]

  fe --1. user question +\nchat history--> be
  be --2. user question--> eg
  eg --3. embedding-->be
  be --4. similarity search-->vs
  vs --5. similar docs-->be
  be --6. user question +\nchat history +\nsimilar docs-->llm
  llm --7. bot answer--> be
  be --8. bot answer--> fe
```

## Vector Index

The application will check if the collection includes at Vector Search Index at startup. If it does not find it, it will create a new one. If there's already one, it will try to update if notices that there any difference between the existing one and the one based on the values included in the [configuration](#configuration) file.

The Vector Search Index will have the following structure:

```json
{
  "fields": [
    {
      "numDimensions": <numDimensions>,
      "path": "<embeddingKey>",
      "similarity": "<relevanceScoreFn>",
      "type": "vector"
    }
  ]
}
```

The values `numDimensions`, `embeddingKey` and `relevanceScoreFn` comes from the [configuration file](#configuration). While `embeddingKey` and `relevanceScoreFn` comes exactly from the values included in the file, the `numDimensions` depends on the Embedding Model used (supported: `text-embedding-3-small` and `text-embedding-3-large`).

> **NOTE**
>
> In the event that an error occurs during the creation or update of the Vector Index, the exception will be logged, but the application will still start. However, the functioning of the service is not guaranteed.

## Configuration

The service requires several configuration parameters for execution. Below is an example of configuration:

```json
{
  "llm": {
    "type": "openai",
    "name": "gpt-3.5-turbo",
    "temperature": 0.7,
  },
  "embeddings": {
    "type": "openai",
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

| Param Name | Description |
|------------|-------------|
| LLM Type | Identifier of the provider to use for the LLM. Default: `openai`. See more in [Supported LLM providers](#supported-llm-providers) |
| LLM Name | Name of the chat model to use. [Must be supported by LangChain.](https://python.langchain.com/docs/integrations/chat/) |
| LLM Temperature | Temperature parameter for the LLM, intended as the grade of variability and randomness of the generated response. Default: `0.7` (suggested value). |
| Embeddings Type | Identifier of the provider to use for the Embeddings. Default: `openai`. See more in [Supported Embeddings providers](#supported-embeddings-providers) |
| Embeddings Name | Name of the encoder to use. [Must be supported by LangChain.](https://python.langchain.com/docs/integrations/text_embedding/) |
| Vector Store DB Name | Name of the MongoDB database to use as a knowledge base. |
| Vector Store Collection Name | Name of the MongoDB collection to use for storing documents and document embeddings. |
| Vector Store Index Name | Name of the vector index to use for retrieving documents related to the user's query. The application will check at startup if a vector index with this name exists, it needs to be updated or needs to be created. |
| Vector Store Relevance Score Function | Name of the similarity function used for extracting similar documents using the created vector index. In case the existing vector index uses a different similarity function, the index will be updated using this as a similarity function. |
| Vector Store Embeddings Key | Name of the field used to save the semantic encoding of documents. In case the existing vector index uses a different key to store the embedding in the collection, the index will be updated using this as key. Please mind that any change of this value might require to recreate the embeddings. |
| Vector Store Text Key | Name of the field used to save the raw document (or chunk of document). |
| Vector Store Max. Documents To Retrieve | Maximum number of documents to retrieve from the Vector Store. |
| Vector Store Min. Score Distance | Minimum distance beyond which retrieved documents from the Vector Store are discarded. |
| Chain Aggregate Max Token Number | Maximum number of tokens extracted from the retrieved documents from the Vector Store to be included in the prompt (1 token is approximately 4 characters). Default is `2000`. |
| Chain RAG System Prompts File Path | Path to the file containing system prompts for the RAG model. If omitted, the application will use a standard system prompt. More details in the [dedicated paragraph](#configure-your-own-system-and-user-prompts). |
| Chain RAG User Prompts File Path | Path to the file containing user prompts for the RAG model. If omitted, the application will use a standard system prompt. More details in the [dedicated paragraph](#configure-your-own-system-and-user-prompts). |

### Supported LLM providers

The property `type` inside the `llm` object of the configuration should be one of the supported providers for the LLM.
Currently, the supported LLM providers are:

- OpenAI (`openai`), in which case the `llm` configuration could be the following:
  ```json
  {
    "type": "openai",
    "name": "gpt-3.5-turbo",
    "temperature": 0.7,
  }
  ```
  with the properties explained above.

- Azure OpenAI (`azure`), in which case the `llm` configuration could be the following:
  ```json
  {
    "type": "azure",
    "name": "gpt-3.5-turbo",
    "deploymentName": "dep-gpt-3.5-turbo",
    "url": "https://my-company.openai.azure.com/",
    "apiVersion": "my-azure-api-version",
    "temperature": 0.7
  }
  ```

  While, `type` is always `azure`, and `name` and `temperature` have been already explained, the other properties are:
  | Name |  Description |
  |------|-------------|
  | `deploymentName` | Name of the deployment to use. |
  | `url` | URL of the Azure OpenAI service to call. |
  | `apiVersion` | API version of the Azure OpenAI service. |

### Supported Embeddings providers

The property `type` inside the `embeddings` object of the configuration should be one of the supported providers for the Embeddings.
Currently, the supported Embeddings providers are:

- OpenAI (`openai`), in which case the `embeddings` configuration could be the following:
  ```json
  {
    "type": "openai",
    "name": "text-embedding-3-small",
  }
  ```
  with the properties explained above.

  - Azure OpenAI (`azure`), in which case the `embeddings` configuration could be the following:
  ```json
  {
    "type": "azure",
    "name": "text-embedding-3-small",
    "deploymentName": "dep-text-embedding-3-small",
    "url": "https://my-company.openai.azure.com/",
    "apiVersion": "my-azure-api-version"
  }
  ```
  While, `type` is always `azure`, and `name` have been already explained, the other properties are:
  
  | Name |  Description |
  |------|-------------|
  | `deploymentName` | Name of the deployment to use. |
  | `url` | URL of the Azure OpenAI service to call. |
  | `apiVersion` | API version of the Azure OpenAI service. |

### Configure your own system and user prompts

The application sends to the LLM a prompt that is composed of a _system prompt_ and a _user prompt_:

- the _system prompt_ is a message that provides instructions to the LLM on how to respond to the user's input.
- the _user prompt_ is a message that contains the user's input.

A default version of these prompts are included in the application, but you can also use your own prompts to instruct the LLM to behave in a more specific way, such as behaving as a generic assistant in any field or as an expert in a specific field related to the embedding documents you are using.

Both the system and user prompts are optional, but if you want to use your own prompts, you need to create a text file with the content of the prompt and specify the path to the file in the configuration at `chain.rag.systemPromptsFilePath` and `chain.rag.userPromptsFilePath` respectively.

Moreover, the _system prompt_ must include the following placeholders:

- `{chat_history}`: placeholder that will be replaced by the chat history, which is a list of messages exchanged between the user and the chatbot until then (received via the `chat_history` property from the body of the [`/chat/completions` endpoint](#chat-endpoint-chatcompletions))
- `{output_text}`: placeholder that will be replaced by the text extracted from the embedding documents

> **Note**
>
> The application already includes some context text to explain what the chat history is and what the output text is, so you don't need to add your explanation to the system prompt.

Also, the _user prompt_ must include the following placeholder:

- `{query}`: placeholder that will be replaced by the user's input (received via the `chat_query` property from the body of the [`/chat/completions` endpoint](#chat-endpoint-chatcompletions))

Generally speaking, it is suggested to have a _system prompt_ tailored to the needs of your application, to specify what type of information the chatbot should provide and the tone and style of the responses. The _user prompt_ can be omitted unless you need to specify particular instructions or constraints specific to each question.

## Local Development

- Before getting started, make sure you have the following information:
  - A valid connection string to connect to MongoDB Atlas
  - An OpenAI API Key to generate embeddings and contact the chat model (it's better to use two different keys)

- Copy the sample environment variables into a file used for development and replace the placeholders with your own values. As example you can create a file called `local.env` from `default.env` with the following command:

```sh
cp default.env local.env
```

- Modify the values of the environment variables in the newly created file (for more info, refer to the [Overview and Usage](./docs/10_Overview_And_Usage.md#environment-variables) page)
- Create a configuration file located in the path defined as the `CONFIGURATION_PATH` value in the environment variables file. As example, you can copy the `default.configuration.json` file into a new file called `local.configuration.json` with the following command:

```sh
cp default.configuration.json local.configuration.json
```

- Modify the values of the configuration in the newly created file, accordingly to the definitions included in the [Overview and Usage](./docs/10_Overview_And_Usage.md#configuration) page.

### Startup

- Create a virtual environment to install project dependencies

```sh
python3 -m venv .venv
```

- Activate the new virtual environment

```sh
source .venv/bin/activate
```

- Install project dependencies

```sh
make install
```

You can run the web server with this command

```sh
# This uses the environment variable located to `local.env`
make start
# Or you can run:
dotenv -f <<YOUR_ENV_FILE>> run -- python -m src.app
```

You can reivew the API using the Swagger UI exposed at `http://localhost:3000/docs`

### Contributing

To contribute to the project, please always create a branch for your updates and submit a Merge Request requesting approvals for one of the maintainers of the repository.

In order to push your commit, pre-commit operations are automatically executed to run unit tests and lint your code.

#### Unit tests

Ensure at any time that unit tests passes successfully. You can verify that via:

```sh
make test
```

Some of our tests includes snapshot, that can be updated via

```sh
make snapshot
```

> **NOTE**: you might need to run `make test` again after updating the snapshots

Please make sure you include new tests or update the existing ones, according to the feature you are working on.

#### Lint

We use [pylint](https://pypi.org/project/pylint/) as a linter. Please, try to follow the lint rules. You can run:

```sh
make lint
```

to make sure that code and tests follow our lint guidelines.

To fix any issue you can run

```sh
make lint-fix
```

or manually fix your code according to the errors and warning received.

#### Add new dependencies

You can add new dependencies, according to your needs, with the following command:

```sh
python -m pip install <<module_name>>
```

However, the package manager `pip` does not update automatically the list of dependencies included in the `requirements.txt` file. You have to do it by yourself with:

```sh
make freeze
# Or:
python -m pip freeze > requirements.txt
```

### Startup with Docker

If you prefer Docker...

- Build your image

```sh
docker build . -t ai-rag-template
```

- Run the web server

```sh
docker run --env-file ./local.env -p 3000:3000 -d ai-rag-template
```
