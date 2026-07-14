#!/bin/sh
set -e

python manage.py migrate --noinput

celery -A config worker --loglevel=info --concurrency=2 &

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000