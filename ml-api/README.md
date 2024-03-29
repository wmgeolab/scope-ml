# Scope-ML / ML-Api

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
