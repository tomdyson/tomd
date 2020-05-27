#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Start Gunicorn processes
exec gunicorn tomd.wsgi:application --bind 0.0.0.0:$PORT