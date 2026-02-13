# Use a slim python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload the sentiment model (baked into image for instant startup)
COPY preload_model.py .
RUN python preload_model.py

# Copy the application
COPY . .

# Create data directories
RUN mkdir -p /app/sessions /app/data

# Default port (overridden per service in docker-compose)
EXPOSE 5000
EXPOSE 5001

# Default command (overridden by docker-compose)
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
