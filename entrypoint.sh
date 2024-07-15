#!/bin/sh
sleep 5  # This is just to ensure the postgres is fully up and running.
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
exec "$@"
