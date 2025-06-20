#!/bin/sh

echo "Starting backend services..."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Checking file system structure..."
echo "Current directory: $(pwd)"
echo "Listing contents of /app directory:"
find /app -type f -name "ingredients.json" | sort
find /app -type d -name "data" | sort
ls -la /app

echo "Importing ingredients..."
python manage.py import_ingredients --json --path=/app/data/ingredients.json

echo "Starting Gunicorn server..."
exec gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
