#!/bin/sh

python manage.py tailwind build --no-input;
python manage.py collectstatic --no-input
python manage.py migrate --no-input

exec "$@"