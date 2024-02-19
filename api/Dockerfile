# Use the official Python base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

RUN pip install poetry

# Copy the requirements file to the container
COPY pyproject.toml ./
COPY poetry.lock ./
COPY poetry.toml ./

# Install the project dependencies
# RUN poetry install --no-root --no-interaction

# COPY .venv/ ./.venv
RUN poetry config virtualenvs.create false

RUN poetry install --no-root --no-interaction

# Copy the project files to the container
COPY app/ ./app

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Start the FastAPI server
# CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

