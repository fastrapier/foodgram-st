#!/bin/sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
