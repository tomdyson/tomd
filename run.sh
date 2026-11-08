#!/bin/bash
set -e
python manage.py migrate                  # Apply database migrations

# Start Gunicorn processes
exec gunicorn tomd.wsgi:application --bind 0.0.0.0:$PORT