# Use a slim python image to keep size reasonable, though Pysentimiento + Torch is large.
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set huggingface cache to a specific dir if we want, but default /root/.cache is fine in container

WORKDIR /app

# Install system dependencies if needed (sometimes C++ build tools are needed for some libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Preload the model so it's baked into the image
# This increases build time but makes startup instant
COPY preload_model.py .
RUN python preload_model.py

# Copy the rest of the application
COPY . .

# Expose port
EXPOSE 5000

# Run with Gunicorn
# -w 1: Use 1 worker because the model is heavy and loads into memory. 
# If you have a lot of RAM, you can increase this, but 1 is safe for entry-level VPS.
# --timeout 120: Loading the model might take time on slow systems.
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "app:app", "--timeout", "120"]
