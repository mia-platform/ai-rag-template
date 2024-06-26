# mia_template_service_name_placeholder

[![Python
version](https://img.shields.io/badge/python-v3.11.9-blue)](.coverage/html/index.html)
[![FastAPI
version](https://img.shields.io/badge/fastapi-v0.110.1-blue)](.coverage/html/index.html)

---

mia_template_service_name_placeholder is a template meant to be a based for the implementation of a RAG (retrieval augmented generation) system.  
This repository contains the backend code, which consists of a web server that provides REST APIs to primarily support one type of operation:

- **Chat**: Provides a conversation feature, allowing users to ask questions and get responses from the chatbot.

The backend was developed using the [LangChain](https://python.langchain.com/docs/get_started/introduction/) framework, which enables creating sequences of complex interactions using Large Language Models. The web server was implemented using the [FastAPI](https://fastapi.tiangolo.com/) framework.

## Local Development

- Before getting started, make sure you have the following information:
  - A valid connection string to connect to MongoDB Atlas
  - An OpenAI API Key to generate embeddings and contact the chat model (it's better to use two different keys)

- Copy the sample environment variables into a file used for development and replace the placeholders with your own values. As example you can create a file called `local.env` from `default.env` with the following command:

```sh
cp default.env local.env
```

- Modify the values of the environment variables in the newly created file
- Create a configuration file located in the path defined as the `CONFIGURATION_PATH` value in the environment variables file. As example, you can copy the `default.configuration.json` file into a new file called `local.configuration.json` with the following command:

```sh
cp default.configuration.json local.configuration.json
```

- Modify the values of the configuration in the newly created file, accordingly to the definitions included in the [Configuration paragraph](#configuration)

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

### Try the ai-rag-template

You can also use the ai-rag-template with a CLI. Please follow the instruction in the [related README file](./scripts/chatbotcli/README.md).
