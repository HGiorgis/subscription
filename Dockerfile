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
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p /app/static /app/media /app/logs

# Create entrypoint script
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
echo "Waiting for database..."\n\
while ! nc -z db 5432; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Creating superuser if not exists..."\n\
python manage.py shell <<EOF\n\
from django.contrib.auth import get_user_model\n\
import os\n\
User = get_user_model()\n\
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")\n\
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")\n\
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")\n\
if not User.objects.filter(username=username).exists():\n\
    User.objects.create_superuser(username, email, password)\n\
    print(f"Superuser {username} created")\n\
else:\n\
    print(f"Superuser {username} already exists")\n\
EOF\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
echo "Seeding plans..."\n\
python manage.py seed_plans --users 2 || echo "Seed plans skipped or failed"\n\
\n\
echo "Seeding premium content..."\n\
python manage.py seed_premium || echo "Seed premium skipped or failed"\n\
\n\
echo "Starting server..."\n\
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers 4\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port
EXPOSE ${PORT}

# Run entrypoint
CMD ["/app/entrypoint.sh"]