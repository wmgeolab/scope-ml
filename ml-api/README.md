# Scope-ML / ML-Api

Implements an api server that responds to requests for document summarization and question answering from the scope backend.

Currently only set up to work with gef documents.

## src\ml_api\api

router.py implements the api endpoints designed to be called by the scope backend.

### Example: request for question answering using the ml api service on the cluster

```
curl -X POST "http://ml-api-svc:8000/generate_rag_response" \
     -H "Content-Type: application/json" \
     -d '{"question": "What cities in Barbuda are mentioned", "source": "18341", "workspace": "310"}'
```

schemas.py defines pydantic models for the correct form of inputs and outputs.

tasks.py handles background tasks that cannot be completed in a single request. Currently includes tasks for returning information to the scope backend and ingesting documents into the Qdrant database.

## src\ml_api\ingestion

Code for inserting documents into the Qdrant vector database.

This includes parsing the raw document to text, chunking the text with metadata,
and indexing the chunks into the Qdrant database to be used in inference.

## src\ml_api\retrieval

Code for retrieving chunks from the Qdrant database.

This includes filtering Qdrant queries by metadata, possibly reranking the results,
possibly rewriting the query to something more suitable for knowledge retrieval, and
returning the results.

## src\ml_api\rag_inference

Responds to a query and generates an answer using Retrieval Augmented Generation (RAG)

This includes interacting with the retrieval service to get relevant information and interacting with the
vLLM service to generate an answer.

## src\ml_api\utils

Assorted utility files.

# TODO - how to use different llms

# TODO - how to run/test the api locally and on the cluster

cloudflare stuff?

# Old README:

## WSL 2

It is recommended to use WSL 2 to run the api. Follow the instructions from the [WSL 2 Docs](https://docs.microsoft.com/en-us/windows/wsl/install) to install WSL 2. It is recommended to use Ubuntu.

After installing Ubuntu on WSL, start the instance and install:

- git
- github cli (optional, makes git auth easier)
- poetry
- pyenv (optional, to install specific python version easier)
- python 3.11

## Installing the correct version of python

<!-- Install pyenv  -->

This project uses `python 3.11`. To install the correct version of python, run this command from the `/ml-api` directory:

```bash
pyenv install 3.11.8
```

## Install & Activate the Environment

First you have to install `poetry`. Follow the instructions from the [Poetry Docs](https://python-poetry.org/docs/#installation).

Then to install the packages, run this command from the `/ml-api` directory:

```bash
poetry install
```

To activate the environment, run this command from the `/ml-api` directory:

```bash
poetry shell
```

## Installing SQL

```bash
sudo apt-get install libmysqlclient-dev
```

## Run the api

After activating the environment, run this command from the `/ml-api` directory to start the api:

```bash
uvicorn app.main:app --reload
```
