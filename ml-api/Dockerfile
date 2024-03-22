# Use the official Python base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /ml-api

RUN pip install poetry
RUN poetry config virtualenvs.create false

# Copy the requirements file to the container
COPY pyproject.toml ./
COPY poetry.lock ./

# Install the project dependencies
RUN poetry install --no-root --no-interaction

# Copy the project files to the container
COPY ml_api/ ./ml_api

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "ml_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

