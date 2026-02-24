#!/bin/sh
set -e

# Run database migrations
python manage.py migrate --noinput

# Collect static files (optional)
# python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
