# Build stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPYCACHEPREFIX=/var/cache/python \
    POETRY_VERSION=1.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry --version

# Set the working directory
WORKDIR /app

# Copy only the files needed for installation
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the project files
COPY . .

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPYCACHEPREFIX=/var/cache/python

# Create and set permissions for Python cache directory
RUN mkdir -p /var/cache/python && chmod -R 777 /var/cache/python

# Set the working directory
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Set the PATH to include the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/src

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "ml_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]


# test