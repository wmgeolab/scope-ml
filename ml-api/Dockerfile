# Use the official Python base image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPYCACHEPREFIX=/var/cache/python

# Create and set permissions for Python cache directory
RUN mkdir -p /var/cache/python && chmod -R 777 /var/cache/python

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry & Configure poetry
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

# Copy poetry files & install dependencies
COPY pyproject.toml poetry.lock poetry.toml ./
RUN poetry install --no-interaction --no-root
RUN poetry install --no-interaction

# Copy the project files to the container
COPY . .

WORKDIR /app/src

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Start the FastAPI server
CMD ["poetry", "run", "uvicorn", "ml_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]