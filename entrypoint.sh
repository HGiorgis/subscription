#!/bin/sh
set -e

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser if not exists..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123")
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created")
else:
    print(f"Superuser {username} already exists")
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Seeding plans..."
python manage.py seed_plans --users 2 || echo "Seed plans skipped or failed"

echo "Seeding premium content..."
python manage.py seed_premium || echo "Seed premium skipped or failed"

echo "Starting server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4