#!/bin/bash

python manage.py makemigrations
python manage.py migrate

gunicorn -w 4 -k uvicorn.workers.UvicornWorker config.asgi:application --bind 0.0.0.0:8000