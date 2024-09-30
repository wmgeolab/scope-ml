# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install Firefox and GeckoDriver
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install GeckoDriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
    && tar -xvzf geckodriver-v0.30.0-linux64.tar.gz \
    && chmod +x geckodriver \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-v0.30.0-linux64.tar.gz

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

# Create directories for data and output
RUN mkdir -p /app/data/output /app/data/debug

# Set environment variables
ENV PROJECTS_CSV_PATH=/app/data/projects.csv
ENV OUTPUT_PATH=/app/data/output
ENV JSON_PATH=/app/data/project_ids.json
ENV DB_PATH=/app/data/scraper.db

# Run the script when the container launches
CMD ["python", "gef_portal_scraper/get_projects_csv_selen.py"]