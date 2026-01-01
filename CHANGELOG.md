# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## Changed

- Using Python v3.13
- Using [`uv`](https://github.com/astral-sh/uv) as a package and project manager
- Using [`ruff`](https://docs.astral.sh/ruff/) as a linter
- Updated several key libraries for the application to startup (Uvicorn, FastAPI, Starlette, requests, urllib3)
- Updated library _datamodel-code-generator_ to improve generation of Python definitions from JSON Schema
to validate the configuration file
- Updated langchain dependencies to solve vulnerability issues

## 0.5.3 - 2025-02-07

### Fixed

- Version `0.5.2` included an error with the `mdx` files for embedding generation from `generateFromFile` API. This has been fixed.
- Fixed several typos related to the `aggregateMaxTokenNumber` configurable parameter.s

### Changed

- Updated documentation related to the Aggregate Max Token Number and custom prompts (both system and user prompts)

## 0.5.2 - 2025-01-29


### Fixed

- At service startup, if the Vector Search collection does not exist, it is automatically created
- Support file extension `mdx` for embedding generation
- File uploaded for embedding generation is validated either from the content-type or the file extension

## 0.5.1 - 2024-12-20

## 0.5.0 - 2024-12-19

### Added

- Created new pipeline flow for testing, linting, security (with `bandit` and `pip-audit`) and docker image publishing on tags.

## 0.4.0 - 2024-12-18

- updated dependencies (FastAPI, Langchain, OpenAI)

### Added

- add endpoint `POST /embeddings/generateFromFile` for embedding generation
- add support for _Azure OpenAI_ provider for embedding generation and LLM usage

## 0.3.1 - 2024-09-05

## 0.3.0 - 2024-09-05

### Added

- Automatic creation/update of the Vector Index
- add endpoints `POST /embeddings/generate` and `GET /embeddings/status` for embedding generation

## 0.2.0 - 2024-08-21

### Updated

- updated dependencies (FastAPI, Langchain, OpenAI)
- the application is now using Python version 3.12.3
- improved documentation

## 0.1.1 - 2024-05-09

### Added

- first template implementation
