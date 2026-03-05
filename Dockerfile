# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements-docker.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements-docker.txt

# Upgrade Stripe to ensure compatibility with latest API versions
RUN pip install --upgrade stripe

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/media /app/logs

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE ${PORT}

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]