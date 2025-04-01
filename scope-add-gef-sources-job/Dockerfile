FROM python:3.12-slim

WORKDIR /app

# Copy requirements file first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY gef_to_scope_db.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run script when container starts
ENTRYPOINT ["python", "gef_to_scope_db.py"]