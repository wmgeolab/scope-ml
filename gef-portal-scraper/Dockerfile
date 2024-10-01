# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the project code
COPY gef_portal_scraper/ ./gef_portal_scraper/
COPY data/ ./data/

# Create directories for data and output
RUN mkdir -p /app/data/output

# Set environment variables
ENV PROJECTS_CSV_PATH=/app/data/projects.csv
ENV OUTPUT_PATH=/app/data/output
ENV JSON_PATH=/app/data/project_ids.json
ENV DB_PATH=/app/data/scraper.db

# Run the script when the container launches
CMD ["python", "gef_portal_scraper/gef_portal_scraper.py"]