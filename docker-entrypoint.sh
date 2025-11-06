#!/bin/bash
set -e

# Создаем необходимые директории с правильными правами
echo "Setting up media directories..."
mkdir -p /app/media/theory/images
chmod -R 777 /app/media
chown -R "$(whoami)":"$(whoami)" /app/media 2>/dev/null || true

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec "$@"